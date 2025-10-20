# GitAuto

A sleek, lightweight Git automation tool for Windows that streamlines your development workflow with a modern, draggable interface.

![GitAuto Interface](https://img.shields.io/badge/Platform-Windows-blue) ![GitAuto Version](https://img.shields.io/badge/Version-0.2.9.6-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- **One-Click Git Operations** - Push, pull, status, restore, and reset with a single click
- **Modern Dark UI** - Clean, professional interface built with CustomTkinter
- **Auto-Versioning** - Intelligent version management with semantic versioning
- **Draggable Window** - Move the app anywhere on your screen
- **Right-Click Context Menu** - Quick access to all Git commands
- **Repository Management** - Easy setup and switching between Git repositories
- **Standalone Executable** - No Python installation required

## 🚀 Quick Start

### Download & Install

1. **Download the latest release** from the [Releases page](https://github.com/MelgibsonK/GitAuto/releases)
2. **Extract** `GitAuto.exe` to your desired location
3. **Double-click** to run (no installation required)

### First Time Setup

1. **Launch GitAuto** - The app will appear at the top of your screen
2. **Set Repository** - Click "Set Repo" and select your Git project folder
3. **Start Using** - Click "Push" to commit and push changes with auto-versioning

## 📋 Requirements

- **Windows 7/8/10/11** (64-bit recommended)
- **Git** installed on your system
- **No additional software** required

## 🎯 How It Works

### Main Interface
- **Repository Display** - Shows current Git repository name
- **Status Indicator** - Real-time feedback on operations
- **Action Buttons** - Context-sensitive buttons based on repo status

### Right-Click Menu
Access additional Git operations by right-clicking anywhere on the app:

- **📊 Git Status** - View repository status and changes
- **⬇️ Git Pull** - Pull latest changes from remote
- **🔄 Git Restore** - Restore files to last commit
- **⏪ Git Reset --hard** - Reset to specific commit (with commit selector)
- **✕ Close Application** - Exit the application

### Auto-Versioning System
GitAuto automatically manages version numbers using semantic versioning:

- **Patch increments** (0.0.1.0 → 0.0.2.0 → 0.0.3.0...)
- **Minor increments** every 10 patches (0.0.9.0 → 0.1.0.0)
- **Major increments** every 100 commits
- **Build number** stays at 0

## 🛠️ Usage Examples

### Basic Workflow
```
1. Set your Git repository
2. Make changes to your code
3. Click "Push" - GitAuto handles the rest:
   - Adds all changes
   - Commits with auto-generated version
   - Pushes to remote repository
```

### Advanced Operations
- **Check Status**: Right-click → Git Status
- **Pull Changes**: Right-click → Git Pull  
- **Reset to Commit**: Right-click → Git Reset --hard → Select commit
- **Restore Files**: Right-click → Git Restore

## 🔧 Troubleshooting

### Common Issues

**"Git not found" error**
- Ensure Git is installed and added to your system PATH
- Restart GitAuto after installing Git

**"Invalid Repo" error**
- Make sure you select a folder containing a `.git` directory
- Initialize Git repository first: `git init`

**App won't start**
- Check Windows compatibility (Windows 7+)
- Run as administrator if needed
- Ensure no antivirus is blocking the executable

### Getting Help

If you encounter issues:
1. Check the [Issues page](https://github.com/MelgibsonK/GitAuto/issues)
2. Create a new issue with details about your problem
3. Include your Windows version and Git version

## 📁 File Structure

```
GitAuto/
├── GitAuto.exe          # Standalone executable
├── icon.ico             # Application icon
└── README.md            # This file
```

## 🔄 Version History

- **v0.2.9.6** - Current version with full Git automation
- **v0.2.9.5** - Improved UI responsiveness
- **v0.2.9.4** - Added context menu functionality
- **v0.2.9.3** - Enhanced versioning system
- **v0.2.9.2** - Initial release with core features

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Mayson** - *Initial work* - [MelgibsonK](https://github.com/MelgibsonK)

## 🙏 Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for modern UI
- Powered by [PyInstaller](https://pyinstaller.org/) for standalone executables
- Icons and design inspired by modern Git tools

---

**Made with ❤️ for developers who value efficiency and simplicity**

*GitAuto - Because Git should be effortless*
