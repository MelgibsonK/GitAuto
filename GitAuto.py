import os
import re
import subprocess
import threading
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox

CONFIG_FILE = os.path.expanduser("~/.autogit_config.json")
context_menu_open = False

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def revert_to_last_published(repo_path, status_update, show_error_popup):
    def worker():
        try:
            status_update("Reverting to last published...", "#FF9800")
            subprocess.run(["git", "fetch"], cwd=repo_path, check=True,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            # Determine upstream (e.g., origin/main)
            result = subprocess.run([
                    "git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"
                ], cwd=repo_path, capture_output=True, text=True, check=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            upstream = result.stdout.strip()
            # Reset hard to the upstream (last published)
            subprocess.run(["git", "reset", "--hard", upstream], cwd=repo_path, check=True,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            subprocess.run(["git", "clean", "-fd"], cwd=repo_path, check=True,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            # Get the last published commit message to display in green
            msg = subprocess.run([
                    "git", "log", "-1", "--pretty=%B", upstream
                ], cwd=repo_path, capture_output=True, text=True, check=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            last_published_msg = msg.stdout.strip().split('\n')[0] if msg.stdout else "Last successful commit"
            status_update(f"✅ {last_published_msg}", "#00C853")
        except subprocess.CalledProcessError as err:
            status_update("Revert failed", "#E53935")
            err_text = err.stderr.decode() if getattr(err, 'stderr', None) else str(err)
            show_error_popup("Revert Error", f"Failed to revert to last published commit:\n{err_text}")
        except Exception as err:
            status_update("Revert failed", "#E53935")
            show_error_popup("Revert Error", f"Unexpected error:\n{str(err)}")
    threading.Thread(target=worker, daemon=True).start()

def get_latest_version(repo_path):
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        last_msg = result.stdout.strip()
        m = re.search(r"V-(\d+)\.(\d+)\.(\d+)\.(\d+)", last_msg)
        if m:
            major, minor, patch, build = map(int, m.groups())
            patch += 1
            if patch >= 10:
                minor += 1
                patch = 0
            return f"V-{major}.{minor}.{patch}.{build}"
        return "V-0.0.1.0"
    except subprocess.CalledProcessError:
        return "V-0.0.1.0"

def run_git_push(repo_path, status_update, show_error_popup):
    try:
        status_update("Getting version...", "#FFB300")
        new_version = get_latest_version(repo_path)
        status_update(f"Committing {new_version}", "#FFB300")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, 
                      creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        subprocess.run(["git", "commit", "-m", new_version], cwd=repo_path, check=True,
                      creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        subprocess.run(["git", "push"], cwd=repo_path, check=True,
                      creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        status_update(f"✅ {new_version} pushed", "#00C853")
    except subprocess.CalledProcessError as e:
        error_msg = f"Git Error:\n\n{e.stderr.decode() if e.stderr else str(e)}"
        status_update("Git error occurred", "#E53935")
        # After the user acknowledges the error, revert to the last published commit
        show_error_popup("Git Error", error_msg, after_ok=lambda: revert_to_last_published(repo_path, status_update, show_error_popup))
    except Exception as e:
        error_msg = f"Unexpected Error:\n\n{str(e)}"
        status_update("Error occurred", "#E53935")
        show_error_popup("Error", error_msg)

def main():
    config = load_config()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.title("Git Auto")
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    width = 600
    height = 30
    screen_width = root.winfo_screenwidth()
    x = int((screen_width / 2) - (width / 2))
    root.geometry(f"{width}x{height}+{x}+0")
    root.configure(fg_color=("#2B2B2B", "#2B2B2B"))
    main_frame = ctk.CTkFrame(
        root, 
        width=width, 
        height=height,
        corner_radius=15,
        fg_color=("#1E1E1E", "#1E1E1E"),
        border_width=1,
        border_color=("#404040", "#404040")
    )
    main_frame.pack(fill="both", expand=True, padx=2, pady=2)

    def update_status(text, color="#9E9E9E"):
        status_label.configure(text=text, text_color=color)

    def cmd_set_repo():
        path = filedialog.askdirectory(title="Select Git Repo")
        if path and os.path.isdir(os.path.join(path, ".git")):
            config["repo_path"] = path
            save_config(config)
            repo_label.configure(text=os.path.basename(path), text_color="#FFFFFF")
            update_status("Repo saved ✅", "#00C853")
            update_button_layout()
        else:
            messagebox.showerror("Invalid Repo", "Selected folder is not a git repository.")

    def cmd_reset_repo():
        if os.path.exists(CONFIG_FILE):
            try:
                os.remove(CONFIG_FILE)
            except Exception:
                pass
        config.clear()
        repo_label.configure(text="[Not Set]", text_color="#BDBDBD")
        update_status("Repo reset", "#E53935")
        update_button_layout()

    def update_button_layout():
        has_repo = config.get("repo_path") and os.path.isdir(os.path.join(config["repo_path"], ".git"))
        if has_repo:
            push_button.pack(side="right", padx=(3, 5), pady=2)
            set_button.pack_forget()
            reset_button.pack(side="right", padx=(3, 0), pady=2)
        else:
            push_button.pack_forget()
            set_button.pack(side="right", padx=(3, 5), pady=2)
            reset_button.pack(side="right", padx=(3, 0), pady=2)

    def show_error_popup(title, message, after_ok=None):
        def _show_and_then():
            messagebox.showerror(title, message)
            if after_ok:
                after_ok()
        root.after(0, _show_and_then)

    # moved to module scope

    def cmd_push():
        repo_path = config.get("repo_path")
        if not repo_path or not os.path.isdir(os.path.join(repo_path, ".git")):
            messagebox.showerror("No Repo", "Set a valid repository first.")
            return
        threading.Thread(target=lambda: run_git_push(repo_path, update_status, show_error_popup), daemon=True).start()
        update_status("🚀 Pushing...", "#2196F3")

    left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    left_frame.pack(side="left", fill="both", expand=True, padx=15, pady=2)
    repo_text = os.path.basename(config.get("repo_path", "[Not Set]"))
    repo_label = ctk.CTkLabel(
        left_frame,
        text=repo_text,
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color="#E0E0E0"
    )
    repo_label.pack(side="left", padx=(0, 10))
    status_label = ctk.CTkLabel(
        left_frame,
        text="Ready",
        font=ctk.CTkFont(size=9),
        text_color="#9E9E9E"
    )
    status_label.pack(side="left")
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.pack(side="right", padx=15, pady=2)
    push_button = ctk.CTkButton(
        button_frame,
        text="Push",
        width=60,
        height=20,
        corner_radius=10,
        font=ctk.CTkFont(size=9, weight="bold"),
        fg_color="#0078D7",
        hover_color="#0A84FF",
        command=cmd_push
    )
    set_button = ctk.CTkButton(
        button_frame,
        text="Set Repo",
        width=70,
        height=20,
        corner_radius=10,
        font=ctk.CTkFont(size=9, weight="bold"),
        fg_color="#424242",
        hover_color="#636363",
        command=cmd_set_repo
    )
    reset_button = ctk.CTkButton(
        button_frame,
        text="Reset",
        width=50,
        height=20,
        corner_radius=10,
        font=ctk.CTkFont(size=9, weight="bold"),
        fg_color="#A33",
        hover_color="#C44",
        command=cmd_reset_repo
    )

    def start_move(event):
        root.x = event.x
        root.y = event.y

    def stop_move(event):
        root.x = None
        root.y = None

    def do_move(event):
        deltax = event.x - root.x
        deltay = event.y - root.y
        x = root.winfo_x() + deltax
        y = root.winfo_y() + deltay
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = root.winfo_width()
        window_height = root.winfo_height()
        x = max(0, min(x, screen_width - window_width))
        y = max(0, min(y, screen_height - window_height))
        root.geometry(f"+{x}+{y}")

    main_frame.bind("<Button-1>", start_move)
    main_frame.bind("<ButtonRelease-1>", stop_move)
    main_frame.bind("<B1-Motion>", do_move)
    left_frame.bind("<Button-1>", start_move)
    left_frame.bind("<ButtonRelease-1>", stop_move)
    left_frame.bind("<B1-Motion>", do_move)

    def cmd_git_status():
        repo_path = config.get("repo_path")
        if not repo_path or not os.path.isdir(os.path.join(repo_path, ".git")):
            messagebox.showerror("No Repo", "Set a valid repository first.")
            return
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            status_output = result.stdout.strip()
            if status_output:
                messagebox.showinfo("Git Status", f"Repository: {os.path.basename(repo_path)}\n\n{status_output}")
            else:
                messagebox.showinfo("Git Status", f"Repository: {os.path.basename(repo_path)}\n\nWorking tree clean - no changes to commit")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Git Error", f"Failed to get git status:\n{e.stderr.decode() if e.stderr else str(e)}")

    def cmd_git_pull():
        repo_path = config.get("repo_path")
        if not repo_path or not os.path.isdir(os.path.join(repo_path, ".git")):
            messagebox.showerror("No Repo", "Set a valid repository first.")
            return
        def run_pull():
            try:
                update_status("Pulling changes...", "#2196F3")
                result = subprocess.run(
                    ["git", "pull"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                update_status("Pull successful ✅", "#00C853")
                messagebox.showinfo("Git Pull", "Successfully pulled latest changes!")
            except subprocess.CalledProcessError as e:
                update_status("Pull failed", "#E53935")
                messagebox.showerror("Git Pull Error", f"Failed to pull changes:\n{e.stderr.decode() if e.stderr else str(e)}")
        threading.Thread(target=run_pull, daemon=True).start()

    def cmd_git_restore():
        repo_path = config.get("repo_path")
        if not repo_path or not os.path.isdir(os.path.join(repo_path, ".git")):
            messagebox.showerror("No Repo", "Set a valid repository first.")
            return
        if messagebox.askyesno("Confirm Restore", "This will restore all files to the last commit and delete untracked files.\n\nAre you sure?"):
            def run_restore():
                try:
                    update_status("Restoring files...", "#FF9800")
                    subprocess.run(["git", "restore", "."], cwd=repo_path, check=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                    subprocess.run(["git", "clean", "-fd"], cwd=repo_path, check=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                    update_status("Restore complete ✅", "#00C853")
                    messagebox.showinfo("Git Restore", "Successfully restored to last commit!")
                except subprocess.CalledProcessError as e:
                    update_status("Restore failed", "#E53935")
                    messagebox.showerror("Git Restore Error", f"Failed to restore files:\n{e.stderr.decode() if e.stderr else str(e)}")
            threading.Thread(target=run_restore, daemon=True).start()

    def cmd_git_reset_hard():
        repo_path = config.get("repo_path")
        if not repo_path or not os.path.isdir(os.path.join(repo_path, ".git")):
            messagebox.showerror("No Repo", "Set a valid repository first.")
            return
        choice_dialog = ctk.CTkToplevel(root)
        choice_dialog.title("Git Reset --hard")
        choice_dialog.geometry("400x200")
        choice_dialog.attributes("-topmost", True)
        choice_dialog.configure(fg_color="#1E1E1E")
        choice_dialog.transient(root)
        choice_dialog.grab_set()
        choice_dialog.geometry("+%d+%d" % (root.winfo_rootx() + 100, root.winfo_rooty() + 100))
        main_frame = ctk.CTkFrame(choice_dialog, fg_color="#1E1E1E")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        title_label = ctk.CTkLabel(
            main_frame,
            text="Choose Reset Method",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(pady=(0, 20))
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)
        def open_commit_selector():
            choice_dialog.destroy()
            show_commit_selector()
        def open_manual_input():
            choice_dialog.destroy()
            show_manual_input()
        select_btn = ctk.CTkButton(
            buttons_frame,
            text="📋 Select from Recent Commits",
            width=300,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#0078D7",
            hover_color="#0A84FF",
            command=open_commit_selector
        )
        select_btn.pack(pady=5)
        manual_btn = ctk.CTkButton(
            buttons_frame,
            text="✏️ Enter Commit Hash Manually",
            width=300,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#424242",
            hover_color="#636363",
            command=open_manual_input
        )
        manual_btn.pack(pady=5)
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            width=100,
            height=30,
            corner_radius=8,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#A33",
            hover_color="#C44",
            command=choice_dialog.destroy
        )
        cancel_btn.pack(pady=(10, 0))
    
    def show_commit_selector():
        repo_path = config.get("repo_path")
        selector_dialog = ctk.CTkToplevel(root)
        selector_dialog.title("Select Commit")
        selector_dialog.geometry("600x400")
        selector_dialog.attributes("-topmost", True)
        selector_dialog.configure(fg_color="#1E1E1E")
        selector_dialog.transient(root)
        selector_dialog.grab_set()
        main_frame = ctk.CTkFrame(selector_dialog, fg_color="#1E1E1E")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        title_label = ctk.CTkLabel(
            main_frame,
            text="Select Commit to Reset To",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(pady=(0, 10))
        def get_recent_commits():
            try:
                result = subprocess.run(
                    ["git", "log", "--oneline", "-20", "--pretty=format:%h|%s|%an|%ar"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|', 3)
                        if len(parts) >= 4:
                            commits.append({
                                'hash': parts[0],
                                'message': parts[1],
                                'author': parts[2],
                                'date': parts[3]
                            })
                return commits
            except subprocess.CalledProcessError:
                return []
        commits = get_recent_commits()
        selected_commit = [None]
        commits_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
        commits_frame.pack(fill="both", expand=True, pady=(0, 10))
        scrollable_frame = ctk.CTkScrollableFrame(commits_frame, fg_color="#2B2B2B")
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        commit_frames = []
        for i, commit in enumerate(commits):
            commit_frame = ctk.CTkFrame(scrollable_frame, fg_color="#404040", corner_radius=5)
            commit_frame.pack(fill="x", pady=2)
            commit_frames.append(commit_frame)
            def create_commit_handler(commit_data, frame):
                def select_commit():
                    selected_commit[0] = commit_data
                    for f in commit_frames:
                        f.configure(fg_color="#404040")
                    frame.configure(fg_color="#0078D7")
                return select_commit
            commit_btn = ctk.CTkButton(
                commit_frame,
                text=f"{commit['hash']} - {commit['message'][:50]}{'...' if len(commit['message']) > 50 else ''}",
                font=ctk.CTkFont(size=10),
                fg_color="transparent",
                hover_color="#505050",
                command=create_commit_handler(commit, commit_frame),
                anchor="w"
            )
            commit_btn.pack(fill="x", padx=5, pady=2)
            info_label = ctk.CTkLabel(
                commit_frame,
                text=f"by {commit['author']} • {commit['date']}",
                font=ctk.CTkFont(size=8),
                text_color="#9E9E9E"
            )
            info_label.pack(anchor="w", padx=10, pady=(0, 5))
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        def confirm_selection():
            if not selected_commit[0]:
                messagebox.showerror("No Selection", "Please select a commit.")
                return
            commit_hash = selected_commit[0]['hash']
            selector_dialog.destroy()
            execute_reset(commit_hash)
        def cancel_selection():
            selector_dialog.destroy()
        confirm_btn = ctk.CTkButton(
            buttons_frame,
            text="Reset to Selected Commit",
            width=150,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#A33",
            hover_color="#C44",
            command=confirm_selection
        )
        confirm_btn.pack(side="right", padx=(5, 0))
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            width=100,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#424242",
            hover_color="#636363",
            command=cancel_selection
        )
        cancel_btn.pack(side="right")
    
    def show_manual_input():
        input_dialog = ctk.CTkToplevel(root)
        input_dialog.title("Enter Commit Hash")
        input_dialog.geometry("400x200")
        input_dialog.attributes("-topmost", True)
        input_dialog.configure(fg_color="#1E1E1E")
        input_dialog.transient(root)
        input_dialog.grab_set()
        main_frame = ctk.CTkFrame(input_dialog, fg_color="#1E1E1E")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        title_label = ctk.CTkLabel(
            main_frame,
            text="Enter Commit Hash",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(pady=(0, 20))
        input_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
        input_frame.pack(fill="x", pady=(0, 20))
        hash_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter commit hash...",
            width=350,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        hash_entry.pack(pady=15)
        hash_entry.focus()
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        def confirm_input():
            commit_hash = hash_entry.get().strip()
            if not commit_hash:
                messagebox.showerror("No Input", "Please enter a commit hash.")
                return
            input_dialog.destroy()
            execute_reset(commit_hash)
        def cancel_input():
            input_dialog.destroy()
        def on_enter(event):
            confirm_input()
        hash_entry.bind("<Return>", on_enter)
        confirm_btn = ctk.CTkButton(
            buttons_frame,
            text="Reset to Hash",
            width=120,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#A33",
            hover_color="#C44",
            command=confirm_input
        )
        confirm_btn.pack(side="right", padx=(5, 0))
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            width=100,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#424242",
            hover_color="#636363",
            command=cancel_input
        )
        cancel_btn.pack(side="right")
    
    def execute_reset(commit_hash):
        repo_path = config.get("repo_path")
        if messagebox.askyesno("Confirm Reset", f"This will reset to commit {commit_hash[:8]}... and lose all changes.\n\nAre you sure?"):
            def run_reset():
                try:
                    update_status("Resetting to commit...", "#FF9800")
                    subprocess.run(["git", "reset", "--hard", commit_hash], cwd=repo_path, check=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                    update_status("Reset complete ✅", "#00C853")
                    messagebox.showinfo("Git Reset", f"Successfully reset to commit {commit_hash[:8]}...")
                except subprocess.CalledProcessError as e:
                    update_status("Reset failed", "#E53935")
                    messagebox.showerror("Git Reset Error", f"Failed to reset to commit:\n{e.stderr.decode() if e.stderr else str(e)}")
            threading.Thread(target=run_reset, daemon=True).start()

    def show_context_menu(event):
        global context_menu_open
        if context_menu_open:
            return
        context_menu_open = True
        context_window = ctk.CTkToplevel(root)
        context_window.overrideredirect(True)
        context_window.attributes("-topmost", True)
        context_window.configure(fg_color="#1E1E1E")
        menu_x = event.x_root
        menu_y = event.y_root
        context_window.geometry(f"180x180+{menu_x}+{menu_y}")
        menu_frame = ctk.CTkFrame(context_window, fg_color="#1E1E1E", corner_radius=8)
        menu_frame.pack(fill="both", expand=True, padx=1, pady=1)
        header_label = ctk.CTkLabel(
            menu_frame,
            text="Git Auto",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#FFFFFF"
        )
        header_label.pack(pady=(8, 3))
        separator1 = ctk.CTkFrame(menu_frame, height=1, fg_color="#404040")
        separator1.pack(fill="x", padx=8, pady=3)
        status_btn = ctk.CTkButton(
            menu_frame,
            text="📊 Git Status",
            width=160,
            height=20,
            corner_radius=10,
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color="#424242",
            hover_color="#636363",
            command=lambda: [close_context_menu(), cmd_git_status()]
        )
        status_btn.pack(pady=1)
        pull_btn = ctk.CTkButton(
            menu_frame,
            text="⬇️ Git Pull",
            width=160,
            height=20,
            corner_radius=10,
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color="#424242",
            hover_color="#636363",
            command=lambda: [close_context_menu(), cmd_git_pull()]
        )
        pull_btn.pack(pady=1)
        restore_btn = ctk.CTkButton(
            menu_frame,
            text="🔄 Git Restore",
            width=160,
            height=20,
            corner_radius=10,
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color="#424242",
            hover_color="#636363",
            command=lambda: [close_context_menu(), cmd_git_restore()]
        )
        restore_btn.pack(pady=1)
        reset_btn = ctk.CTkButton(
            menu_frame,
            text="⏪ Git Reset --hard",
            width=160,
            height=20,
            corner_radius=10,
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color="#424242",
            hover_color="#636363",
            command=lambda: [close_context_menu(), cmd_git_reset_hard()]
        )
        reset_btn.pack(pady=1)
        separator2 = ctk.CTkFrame(menu_frame, height=1, fg_color="#404040")
        separator2.pack(fill="x", padx=8, pady=3)
        close_btn = ctk.CTkButton(
            menu_frame,
            text="✕ Close Application",
            width=160,
            height=20,
            corner_radius=10,
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color="#A33",
            hover_color="#C44",
            command=lambda: [close_context_menu(), root.quit()]
        )
        close_btn.pack(pady=(1, 5))
        author_label = ctk.CTkLabel(
            menu_frame,
            text="By Mayson 0.2.9.6",
            font=ctk.CTkFont(size=7),
            text_color="#666666"
        )
        author_label.pack(pady=(0, 3))
        
        def close_context_menu():
            global context_menu_open
            context_menu_open = False
            context_window.destroy()
        
        def close_menu(event):
            close_context_menu()
        
        def close_menu_self(event):
            close_context_menu()
        
        context_window.bind("<Button-1>", close_menu_self)
        root.bind("<Button-1>", close_menu)
        main_frame.bind("<Button-1>", close_menu)
        left_frame.bind("<Button-1>", close_menu)
        button_frame.bind("<Button-1>", close_menu)
        context_window.focus_set()
        context_window.after(10000, close_context_menu)

    main_frame.bind("<Button-3>", show_context_menu)
    left_frame.bind("<Button-3>", show_context_menu)
    button_frame.bind("<Button-3>", show_context_menu)
    root.bind("<Button-3>", show_context_menu)
    push_button.bind("<Button-3>", show_context_menu)
    set_button.bind("<Button-3>", show_context_menu)
    reset_button.bind("<Button-3>", show_context_menu)
    repo_label.bind("<Button-3>", show_context_menu)
    status_label.bind("<Button-3>", show_context_menu)

    if config.get("repo_path"):
        repo_label.configure(text=os.path.basename(config["repo_path"]), text_color="#FFFFFF")
        update_status("Ready", "#9E9E9E")
    else:
        repo_label.configure(text="[Not Set]", text_color="#BDBDBD")
        update_status("Set repo to start", "#9E9E9E")
    
    update_button_layout()
    root.mainloop()

if __name__ == "__main__":
    main()
