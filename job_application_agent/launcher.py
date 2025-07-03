#!/usr/bin/env python3
"""
Job Application Agent Launcher
Choose between Original and Optimized versions
"""

import sys
import os
import subprocess

def print_banner():
    """Print the launcher banner"""
    print("=" * 80)
    print("🎯 JOB APPLICATION AGENT LAUNCHER")
    print("=" * 80)
    print("Choose your preferred version:")
    print()

def print_versions():
    """Print version comparison"""
    print("📋 VERSION COMPARISON:")
    print()
    
    print("1. 🔧 ORIGINAL VERSION (main.py)")
    print("   • Professional, enterprise-style")
    print("   • Multi-platform simultaneous operation")
    print("   • Standard CLI commands")
    print("   • Proven stability")
    print("   • Commands: --start, --run-once, --status, --config")
    print()
    
    print("2. 🚀 OPTIMIZED VERSION (optimized_main.py)")
    print("   • Smart form handling with dynamic question answering")
    print("   • Single platform focus for better results")
    print("   • AI-powered job matching and filtering")
    print("   • Enhanced human-like behavior")
    print("   • Commands: --hunt, --hunt-once, --profile, --test-forms")
    print()
    
    print("🤖 SMART FEATURES (Optimized Only):")
    print("   • Automatically answers: Python experience (3.5 years)")
    print("   • Automatically answers: Current CTC (7 LPA)")
    print("   • Automatically answers: Expected CTC (15 LPA)")
    print("   • Automatically answers: Notice period (1 Month)")
    print("   • Automatically answers: Last working day (End of July 2024)")
    print("   • Pattern recognition for any question order")
    print("   • Human-like typing and behavior")
    print()

def get_user_choice():
    """Get user choice"""
    while True:
        try:
            choice = input("Enter your choice (1 for Original, 2 for Optimized, q to quit): ").strip().lower()
            
            if choice in ['q', 'quit', 'exit']:
                print("👋 Goodbye!")
                sys.exit(0)
            elif choice == '1':
                return 'original'
            elif choice == '2':
                return 'optimized'
            else:
                print("❌ Invalid choice. Please enter 1, 2, or q")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)

def get_command_options(version):
    """Get command options for the selected version"""
    print(f"\n🎯 {version.upper()} VERSION SELECTED")
    print("=" * 50)
    
    if version == 'original':
        print("Available commands:")
        print("1. 🚀 Start automated job hunting (--start)")
        print("2. 🔍 Run single session (--run-once)")
        print("3. 📊 Check status (--status)")
        print("4. ⚙️ Show configuration (--config)")
        print("5. 🔧 Run diagnostics (--diagnose)")
        print("6. 🎮 Interactive mode")
        print("0. 🔙 Back to version selection")
        
        commands = {
            '1': ['python', 'main.py', '--start'],
            '2': ['python', 'main.py', '--run-once'],
            '3': ['python', 'main.py', '--status'],
            '4': ['python', 'main.py', '--config'],
            '5': ['python', 'main.py', '--diagnose'],
            '6': ['python', 'main.py']
        }
    
    else:  # optimized
        print("Available commands:")
        print("1. 🎯 Start intelligent hunting (--hunt)")
        print("2. 🔍 Single hunt session (--hunt-once)")
        print("3. 🌐 Hunt on Naukri only (--hunt-once --platform naukri)")
        print("4. 🌐 Hunt on LinkedIn only (--hunt-once --platform linkedin)")
        print("5. 📊 Hunter status (--status)")
        print("6. 👤 Hunter profile (--profile)")
        print("7. 🧪 Test smart forms (--test-forms)")
        print("8. 🔧 Run diagnostics (--diagnose)")
        print("9. 🎮 Interactive mode")
        print("0. 🔙 Back to version selection")
        
        commands = {
            '1': ['python', 'optimized_main.py', '--hunt'],
            '2': ['python', 'optimized_main.py', '--hunt-once'],
            '3': ['python', 'optimized_main.py', '--hunt-once', '--platform', 'naukri'],
            '4': ['python', 'optimized_main.py', '--hunt-once', '--platform', 'linkedin'],
            '5': ['python', 'optimized_main.py', '--status'],
            '6': ['python', 'optimized_main.py', '--profile'],
            '7': ['python', 'optimized_main.py', '--test-forms'],
            '8': ['python', 'optimized_main.py', '--diagnose'],
            '9': ['python', 'optimized_main.py']
        }
    
    return commands

def execute_command(command):
    """Execute the selected command"""
    try:
        print(f"\n🚀 Executing: {' '.join(command)}")
        print("-" * 50)
        subprocess.run(command, cwd=os.path.dirname(os.path.abspath(__file__)))
    except KeyboardInterrupt:
        print("\n⏹️ Command interrupted by user")
    except Exception as e:
        print(f"❌ Error executing command: {e}")
    
    input("\n📎 Press Enter to continue...")

def main():
    """Main launcher function"""
    while True:
        print_banner()
        print_versions()
        
        version = get_user_choice()
        
        while True:
            commands = get_command_options(version)
            
            try:
                choice = input(f"\nEnter command choice (0-{len(commands)}) or q to quit: ").strip().lower()
                
                if choice in ['q', 'quit', 'exit']:
                    print("👋 Goodbye!")
                    sys.exit(0)
                elif choice == '0':
                    break  # Back to version selection
                elif choice in commands:
                    execute_command(commands[choice])
                else:
                    print("❌ Invalid choice. Please try again.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                sys.exit(0)

if __name__ == "__main__":
    main()