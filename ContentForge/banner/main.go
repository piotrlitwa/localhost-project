package main

import (
	"fmt"
	"os"
	"time"
)

// ANSI color codes
const (
	Reset   = "\033[0m"
	Bold    = "\033[1m"
	Dim     = "\033[2m"
	Red     = "\033[31m"
	Green   = "\033[32m"
	Yellow  = "\033[33m"
	Cyan    = "\033[36m"
	White   = "\033[37m"
	BRed    = "\033[91m"
	BCyan   = "\033[96m"
	BWhite  = "\033[97m"
	BgBlack = "\033[40m"
)

func typePrint(text string, delay time.Duration) {
	for _, ch := range text {
		fmt.Print(string(ch))
		time.Sleep(delay)
	}
}

func typeLineln(text string, delay time.Duration) {
	typePrint(text, delay)
	fmt.Println()
}

func printBanner() {
	d := 4 * time.Millisecond

	// Brand of Sacrifice inspired border
	sacrifice := Bold + Red + "◆" + Reset
	borderLine := ""
	for i := 0; i < 58; i++ {
		borderLine += "━"
	}

	fmt.Println()
	typeLineln(sacrifice+Bold+Red+borderLine+sacrifice+Reset, d/4)
	fmt.Println()

	// Main ASCII art - BERSERK in aggressive style
	logo := []string{
		`  ██████╗ ███████╗██████╗ ███████╗███████╗██████╗ ██╗  ██╗`,
		`  ██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗██║ ██╔╝`,
		`  ██████╔╝█████╗  ██████╔╝███████╗█████╗  ██████╔╝█████╔╝ `,
		`  ██╔══██╗██╔══╝  ██╔══██╗╚════██║██╔══╝  ██╔══██╗██╔═██╗ `,
		`  ██████╔╝███████╗██║  ██║███████║███████╗██║  ██║██║  ██╗`,
		`  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝`,
	}

	colors := []string{BRed, Red, BRed, Red, BRed, Red}

	for i, line := range logo {
		typeLineln(Bold+colors[i]+line+Reset, d/3)
	}

	fmt.Println()

	// Brand of Sacrifice symbol
	brandArt := []string{
		`             ╱╲`,
		`            ╱  ╲`,
		`           ╱ ◆◆ ╲`,
		`          ╱ ◆◆◆◆ ╲`,
		`         ╱ ◆◆◆◆◆◆ ╲`,
		`        ╱  ◆◆  ◆◆  ╲`,
		`       ╱   ◆◆  ◆◆   ╲`,
		`      ╱     ◆◆◆◆     ╲`,
		`     ╱       ◆◆       ╲`,
		`    ╱────────────────────╲`,
	}

	for _, line := range brandArt {
		typeLineln(Dim+Red+line+Reset, d/2)
	}

	fmt.Println()

	// Subtitle
	subtitle := "    ⚔  T H E   B L A C K   S W O R D S M A N  ⚔"
	typeLineln(Bold+BWhite+subtitle+Reset, d)

	fmt.Println()

	// Project info
	infoLine := fmt.Sprintf("    ContentForge  │  %s", time.Now().Format("2006-01-02"))
	typeLineln(Dim+Cyan+infoLine+Reset, d)

	// Powered by
	poweredBy := "    Powered by Claude Code"
	typeLineln(Dim+BCyan+poweredBy+Reset, d)

	fmt.Println()

	// Bottom border
	typeLineln(sacrifice+Bold+Red+borderLine+sacrifice+Reset, d/4)
	fmt.Println()
}

func main() {
	// Disable typewriter effect if --fast flag is passed
	for _, arg := range os.Args[1:] {
		if arg == "--fast" || arg == "-f" {
			printBannerFast()
			return
		}
	}
	printBanner()
}

func printBannerFast() {
	sacrifice := Bold + Red + "◆" + Reset
	borderLine := ""
	for i := 0; i < 58; i++ {
		borderLine += "━"
	}

	fmt.Println()
	fmt.Println(sacrifice + Bold + Red + borderLine + sacrifice + Reset)
	fmt.Println()

	logo := []string{
		`  ██████╗ ███████╗██████╗ ███████╗███████╗██████╗ ██╗  ██╗`,
		`  ██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗██║ ██╔╝`,
		`  ██████╔╝█████╗  ██████╔╝███████╗█████╗  ██████╔╝█████╔╝ `,
		`  ██╔══██╗██╔══╝  ██╔══██╗╚════██║██╔══╝  ██╔══██╗██╔═██╗ `,
		`  ██████╔╝███████╗██║  ██║███████║███████╗██║  ██║██║  ██╗`,
		`  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝`,
	}

	colors := []string{BRed, Red, BRed, Red, BRed, Red}

	for i, line := range logo {
		fmt.Println(Bold + colors[i] + line + Reset)
	}

	fmt.Println()

	brandArt := []string{
		`             ╱╲`,
		`            ╱  ╲`,
		`           ╱ ◆◆ ╲`,
		`          ╱ ◆◆◆◆ ╲`,
		`         ╱ ◆◆◆◆◆◆ ╲`,
		`        ╱  ◆◆  ◆◆  ╲`,
		`       ╱   ◆◆  ◆◆   ╲`,
		`      ╱     ◆◆◆◆     ╲`,
		`     ╱       ◆◆       ╲`,
		`    ╱────────────────────╲`,
	}

	for _, line := range brandArt {
		fmt.Println(Dim + Red + line + Reset)
	}

	fmt.Println()
	fmt.Println(Bold + BWhite + "    ⚔  T H E   B L A C K   S W O R D S M A N  ⚔" + Reset)
	fmt.Println()
	fmt.Printf(Dim+Cyan+"    ContentForge  │  %s"+Reset+"\n", time.Now().Format("2006-01-02"))
	fmt.Println(Dim + BCyan + "    Powered by Claude Code" + Reset)
	fmt.Println()
	fmt.Println(sacrifice + Bold + Red + borderLine + sacrifice + Reset)
	fmt.Println()
}
