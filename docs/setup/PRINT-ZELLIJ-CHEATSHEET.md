# How to Print Zellij Cheatsheet

## Step 1: View the Cheatsheet

Open the cheatsheet in your browser or preferred markdown viewer:

```bash
# View in terminal
cat ~/.claude/docs/setup/zellij-cheatsheet.md

# Or open in your default browser:
open ~/.claude/docs/setup/zellij-cheatsheet.md
```

## Step 2: Print to PDF

### macOS (Quick Method)

1. Open the markdown file in a browser or application
1. Press `Cmd + P` to open print dialog
1. Click "PDF" dropdown in bottom-left
1. Select "Save as PDF"
1. Choose location and filename
1. Click "Save"

### macOS (Browser Method)

1. Open the file in your browser (Firefox, Safari, Chrome)
1. Press `Cmd + P`
1. In the print dialog:
   - Destination: "Save as PDF"
   - Format: Portrait or Landscape
   - Margins: Normal or Narrow (for more content)
1. Click "Save"

### Convert to HTML First (Better Formatting)

```bash
# Using pandoc (if installed):
pandoc ~/.claude/docs/setup/zellij-cheatsheet.md -o zellij-cheatsheet.html

# Then open in browser and print
open zellij-cheatsheet.html
```

## Step 3: Print Tips

- **Double-sided printing**: Check printer settings for duplex printing
- **Scaling**: Set to "Fit to page" to ensure everything prints on 1-2 pages
- **Margins**: Use narrow margins to fit more content
- **Color**: Both black & white and color print well (tables have borders)

## Step 4: Keep It Handy

Print the PDF and:

- Keep near your desk
- Post on your monitor
- Add to a binder with other documentation
- Share with team members

______________________________________________________________________

## Alternative: Quick Terminal Reference

Without printing, you can always reference while in terminal:

```bash
# Quick display in terminal
cat ~/.claude/docs/setup/zellij-cheatsheet.md | less

# Or with colors/formatting
glow ~/.claude/docs/setup/zellij-cheatsheet.md
```

______________________________________________________________________

**File Location**: `~/.claude/docs/setup/zellij-cheatsheet.md`
**Related Documentation**: `~/.claude/docs/setup/zellij-session-recovery.md`
