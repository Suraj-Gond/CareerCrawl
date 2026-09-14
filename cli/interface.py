"""
Beautiful CLI interface for CareerCrawl.
Built with Rich library for a professional and colorful experience.
"""

import sys
import os
import webbrowser
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.text import Text
from rich import box

from scraper.hybrid_scraper import HybridScraper
from storage.handlers import DataHandler
from storage.history import SearchHistory
from utils.filters import apply_filters
from utils.stats import compute_statistics
from utils.helpers import shorten_url

# Fix Windows console encoding for emoji/unicode
if sys.platform == 'win32':
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

console = Console(force_terminal=True)


class CLI:
    """Main CLI application class for CareerCrawl."""

    def __init__(self):
        self.scraper = HybridScraper()

    def start(self):
        """Launch the main application loop."""
        self._show_banner()
        self._main_menu_loop()

    def _show_banner(self):
        """Display the startup banner."""
        banner_text = (
            " CAREERCRAWL - Internship & Job Finder\n"
            " Powered by Hybrid Scraping System"
        )
        console.print()
        console.print(Panel.fit(
            f"[bold white]{banner_text}[/bold white]",
            border_style="bold cyan",
            padding=(1, 3),
        ))
        console.print()

    def _main_menu_loop(self):
        """Main menu loop - keeps running until user exits."""
        while True:
            console.print()
            menu_panel = Panel(
                "[bold cyan]1[/] [>>] New Search\n"
                "[bold cyan]2[/] [..] View Saved Files\n"
                "[bold cyan]3[/] [??] Filter Results\n"
                "[bold cyan]4[/] [##] Statistics\n"
                "[bold cyan]5[/] [~~] Search History\n"
                "[bold cyan]6[/] [**] Settings\n"
                "[bold cyan]7[/] [<=] Exit",
                title="[bold white]Main Menu[/bold white]",
                border_style="cyan",
                padding=(1, 2),
            )
            console.print(menu_panel)

            choice = Prompt.ask(
                "[bold]Select an option[/bold]",
                choices=["1", "2", "3", "4", "5", "6", "7"],
                default="1"
            )

            if choice == "1":
                self._new_search()
            elif choice == "2":
                self._view_saved_files()
            elif choice == "3":
                self._filter_results()
            elif choice == "4":
                self._show_statistics()
            elif choice == "5":
                self._show_history()
            elif choice == "6":
                self._show_settings()
            elif choice == "7":
                console.print("\n[bold cyan]Thanks for using CareerCrawl! Good luck with your search![/bold cyan]\n")
                break

    # -----------------------------------------------
    # 1. NEW SEARCH
    # -----------------------------------------------
    def _new_search(self):
        """Perform a new search for internships or jobs."""
        console.print()
        console.print(Panel("[bold]>> New Search[/bold]", border_style="green"))

        job_type = Prompt.ask(
            "Search for",
            choices=["Internship", "Job"],
            default="Internship"
        )
        keyword = Prompt.ask("Enter keyword (e.g., Python, Data Science)")
        location = Prompt.ask("Enter location [dim](press Enter for any)[/dim]", default="")

        console.print()
        with console.status("[bold green]Scraping listings...[/bold green]", spinner="dots"):
            results, method = self.scraper.scrape(
                keyword,
                job_type.lower(),
                location if location else None
            )

        if results:
            # Log search to history
            SearchHistory.log_search(keyword, job_type, location, len(results), method)

            # Show preview
            self._show_preview(results)

            # Ask to save
            console.print()
            if Confirm.ask("[bold]Save these results?[/bold]", default=True):
                paths = DataHandler.save_data(results, job_type)
                if paths:
                    console.print(f"\n[bold green][OK] Saved successfully![/bold green]")
                    console.print(f"  JSON:  [dim]{paths[0]}[/dim]")
                    console.print(f"  Excel: [dim]{paths[1]}[/dim]")

            # Ask to open apply link
            self._offer_apply_link(results)
        else:
            SearchHistory.log_search(keyword, job_type, location, 0, "Failed")
            console.print("\n[bold red][X] No results found. Try different keywords or check your connection.[/bold red]")

    def _show_preview(self, results):
        """Display a rich preview table of scraped results."""
        table = Table(
            title="[bold]Preview Results[/bold]",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold white",
            border_style="cyan",
        )

        table.add_column("#", style="dim", width=3, justify="center")
        table.add_column("Title", style="bold cyan", max_width=30)
        table.add_column("Company", style="magenta", max_width=20)
        table.add_column("Location", style="green", max_width=15)
        table.add_column("Stipend", style="yellow", max_width=15)
        table.add_column("Skills", style="blue", max_width=25)
        table.add_column("Method", style="dim", max_width=10)

        for i, r in enumerate(results, 1):
            skills_str = ", ".join(r.get("skills", [])[:3])
            if len(r.get("skills", [])) > 3:
                skills_str += "..."

            table.add_row(
                str(i),
                r.get("title", "N/A"),
                r.get("company", "N/A"),
                r.get("location", "N/A"),
                r.get("stipend_salary", "N/A"),
                skills_str,
                r.get("method_used", "N/A"),
            )

        console.print()
        console.print(table)

    def _offer_apply_link(self, results):
        """Offer to open an apply link in the browser."""
        valid_results = [r for r in results if r.get("apply_link", "N/A") != "N/A"]
        if not valid_results:
            return

        console.print()
        if Confirm.ask("[bold]Open any apply link in browser?[/bold]", default=False):
            for i, r in enumerate(valid_results, 1):
                console.print(f"  [cyan]{i}[/cyan]. {r['title']} - [dim]{shorten_url(r['apply_link'])}[/dim]")

            try:
                choice = IntPrompt.ask(
                    "Enter listing number",
                    default=1
                )
                if 1 <= choice <= len(valid_results):
                    url = valid_results[choice - 1]["apply_link"]
                    webbrowser.open(url)
                    console.print(f"[green][OK] Opened in browser![/green]")
                else:
                    console.print("[yellow]Invalid selection.[/yellow]")
            except Exception:
                console.print("[yellow]Skipped.[/yellow]")

    # -----------------------------------------------
    # 2. VIEW SAVED FILES
    # -----------------------------------------------
    def _view_saved_files(self):
        """List and navigate saved files."""
        console.print()
        console.print(Panel("[bold][..] Saved Files[/bold]", border_style="blue"))

        file_type = Prompt.ask(
            "View files for",
            choices=["Internship", "Job", "All"],
            default="All"
        )

        jtype = file_type.lower() if file_type != "All" else None
        files_dict = DataHandler.list_saved_files(jtype)

        all_files = []
        for category, files in files_dict.items():
            for f in files:
                f["category"] = category.capitalize()
                all_files.append(f)

        if not all_files:
            console.print("[yellow]No saved files found.[/yellow]")
            return

        # Display file list
        table = Table(
            title="[bold]Saved Files[/bold]",
            box=box.ROUNDED,
            border_style="blue",
        )
        table.add_column("#", style="dim", width=3, justify="center")
        table.add_column("Type", style="cyan", width=12)
        table.add_column("Filename", style="white", max_width=40)
        table.add_column("Size", style="dim", width=8, justify="right")
        table.add_column("Modified", style="dim", width=16)

        for i, f in enumerate(all_files, 1):
            table.add_row(
                str(i),
                f["category"],
                f["filename"],
                f"{f['size_kb']} KB",
                f["modified"],
            )

        console.print(table)

        # Navigate
        console.print()
        try:
            choice = IntPrompt.ask(
                "Enter file number to view (0 to go back)",
                default=0
            )
            if 1 <= choice <= len(all_files):
                selected = all_files[choice - 1]
                data = DataHandler.load_data(selected["path"])
                self._show_preview(data)
                self._offer_apply_link(data)
            elif choice != 0:
                console.print("[yellow]Invalid selection.[/yellow]")
        except Exception:
            pass

    # -----------------------------------------------
    # 3. FILTER RESULTS
    # -----------------------------------------------
    def _filter_results(self):
        """Filter saved data by various criteria."""
        console.print()
        console.print(Panel("[bold][??] Filter Results[/bold]", border_style="yellow"))

        # First, select a file to filter
        files_dict = DataHandler.list_saved_files()
        all_files = []
        for category, files in files_dict.items():
            for f in files:
                f["category"] = category.capitalize()
                all_files.append(f)

        if not all_files:
            console.print("[yellow]No saved files to filter. Run a search first![/yellow]")
            return

        console.print("[dim]Select a file to filter:[/dim]")
        for i, f in enumerate(all_files, 1):
            console.print(f"  [cyan]{i}[/cyan]. [{f['category']}] {f['filename']}")

        try:
            choice = IntPrompt.ask("File number", default=1)
            if not (1 <= choice <= len(all_files)):
                console.print("[yellow]Invalid selection.[/yellow]")
                return
        except Exception:
            return

        data = DataHandler.load_data(all_files[choice - 1]["path"])
        console.print(f"[dim]Loaded {len(data)} listings.[/dim]")

        # Build filter criteria
        filters = {}
        console.print()
        console.print("[bold]Enter filter criteria (press Enter to skip):[/bold]")

        skill_input = Prompt.ask("  Skills [dim](comma-separated)[/dim]", default="")
        if skill_input:
            filters["skills"] = [s.strip() for s in skill_input.split(",")]

        location_input = Prompt.ask("  Location", default="")
        if location_input:
            filters["location"] = location_input

        title_input = Prompt.ask("  Title keyword", default="")
        if title_input:
            filters["title_keyword"] = title_input

        min_stipend_input = Prompt.ask("  Min stipend [dim](number, e.g., 5000)[/dim]", default="")
        if min_stipend_input:
            try:
                filters["min_stipend"] = int(min_stipend_input)
            except ValueError:
                pass

        max_stipend_input = Prompt.ask("  Max stipend [dim](number, e.g., 20000)[/dim]", default="")
        if max_stipend_input:
            try:
                filters["max_stipend"] = int(max_stipend_input)
            except ValueError:
                pass

        if not filters:
            console.print("[yellow]No filters applied.[/yellow]")
            return

        # Apply filters
        filtered = apply_filters(data, filters)
        console.print(f"\n[bold green][OK] Found {len(filtered)} matching listings[/bold green] (out of {len(data)})")

        if filtered:
            self._show_preview(filtered)
            self._offer_apply_link(filtered)
        else:
            console.print("[yellow]No listings match your filters.[/yellow]")

    # -----------------------------------------------
    # 4. STATISTICS
    # -----------------------------------------------
    def _show_statistics(self):
        """Show statistics for a saved file."""
        console.print()
        console.print(Panel("[bold][##] Statistics[/bold]", border_style="magenta"))

        files_dict = DataHandler.list_saved_files()
        all_files = []
        for category, files in files_dict.items():
            for f in files:
                f["category"] = category.capitalize()
                all_files.append(f)

        if not all_files:
            console.print("[yellow]No saved files found. Run a search first![/yellow]")
            return

        console.print("[dim]Select a file to analyze:[/dim]")
        for i, f in enumerate(all_files, 1):
            console.print(f"  [cyan]{i}[/cyan]. [{f['category']}] {f['filename']}")

        try:
            choice = IntPrompt.ask("File number", default=1)
            if not (1 <= choice <= len(all_files)):
                console.print("[yellow]Invalid selection.[/yellow]")
                return
        except Exception:
            return

        data = DataHandler.load_data(all_files[choice - 1]["path"])
        stats = compute_statistics(data)

        # Display statistics
        console.print()
        stats_panel_text = (
            f"  Total Listings : [bold]{stats['total']}[/bold]\n"
            f"  Average Stipend: [bold]{stats['average_stipend']}[/bold]\n"
        )
        rvo = stats.get("remote_vs_onsite", {})
        stats_panel_text += f"  Remote: [bold]{rvo.get('remote', 0)}[/bold]  |  Onsite: [bold]{rvo.get('onsite', 0)}[/bold]"

        console.print(Panel(stats_panel_text, title="[bold]Summary[/bold]", border_style="magenta"))

        # Most common skills
        if stats.get("most_common_skills"):
            skills_table = Table(
                title="[bold]Top Skills[/bold]",
                box=box.SIMPLE,
                border_style="blue",
            )
            skills_table.add_column("Skill", style="cyan")
            skills_table.add_column("Count", style="yellow", justify="right")
            for skill, count in stats["most_common_skills"]:
                skills_table.add_row(skill, str(count))
            console.print(skills_table)

        # Location distribution
        if stats.get("location_distribution"):
            loc_table = Table(
                title="[bold]Location Distribution[/bold]",
                box=box.SIMPLE,
                border_style="green",
            )
            loc_table.add_column("Location", style="green")
            loc_table.add_column("Count", style="yellow", justify="right")
            for loc, count in stats["location_distribution"]:
                loc_table.add_row(loc, str(count))
            console.print(loc_table)

    # -----------------------------------------------
    # 5. SEARCH HISTORY
    # -----------------------------------------------
    def _show_history(self):
        """Display search history."""
        console.print()
        console.print(Panel("[bold][~~] Search History[/bold]", border_style="green"))

        history = SearchHistory.get_recent(20)

        if not history:
            console.print("[yellow]No search history yet. Run a search first![/yellow]")
            return

        table = Table(
            title="[bold]Recent Searches[/bold]",
            box=box.ROUNDED,
            border_style="green",
        )
        table.add_column("#", style="dim", width=3, justify="center")
        table.add_column("Date", style="dim", width=19)
        table.add_column("Type", style="cyan", width=12)
        table.add_column("Keyword", style="bold white", max_width=20)
        table.add_column("Location", style="green", max_width=15)
        table.add_column("Results", style="yellow", width=8, justify="right")
        table.add_column("Method", style="dim", width=14)

        for i, entry in enumerate(reversed(history), 1):
            table.add_row(
                str(i),
                entry.get("date", "N/A"),
                entry.get("job_type", "N/A"),
                entry.get("keyword", "N/A"),
                entry.get("location", "Any"),
                str(entry.get("result_count", 0)),
                entry.get("method_used", "N/A"),
            )

        console.print(table)

        console.print()
        if Confirm.ask("[dim]Clear search history?[/dim]", default=False):
            SearchHistory.clear_history()
            console.print("[green][OK] History cleared.[/green]")

    # -----------------------------------------------
    # 6. SETTINGS
    # -----------------------------------------------
    def _show_settings(self):
        """Display current configuration settings."""
        import json

        console.print()
        console.print(Panel("[bold][**] Current Settings[/bold]", border_style="dim"))

        try:
            with open('config.json', 'r') as f:
                config = json.load(f)

            table = Table(box=box.SIMPLE, border_style="dim")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Default Keywords", ", ".join(config.get("default_keywords", [])))
            table.add_row("Results Per Search", str(config.get("results_per_search", 5)))
            delay = config.get("delay_range", [2, 5])
            table.add_row("Delay Range (sec)", f"{delay[0]} - {delay[1]}")
            table.add_row("Default Location", config.get("default_location", "Any"))
            table.add_row("Preferred Method", config.get("preferred_method", "requests"))
            table.add_row("Headless Mode", str(config.get("headless_mode", True)))

            # Show file counts
            counts = DataHandler.get_file_count()
            table.add_row("---", "---")
            table.add_row("Saved Internships", str(counts.get("internship", 0)))
            table.add_row("Saved Jobs", str(counts.get("job", 0)))

            console.print(table)
            console.print("\n[dim]Edit config.json to change settings.[/dim]")
        except FileNotFoundError:
            console.print("[red]config.json not found![/red]")