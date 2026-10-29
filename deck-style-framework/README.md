# Deck style framework (Deep Cut)

One house style for every slide: backgrounds, fonts, colours, title/body sizes.

Files
- `deck_style.json`  the style (edit this to change the look everywhere)
- `style_deck.py`    turns a read of your deck into one Slides batchUpdate that applies the style

House style (matches the PDF deck)
- Font: Nunito. Text colour: navy #131F24. Footnotes: muted #4A555A.
- Content slides: paper background #F6F7F2. Dark layouts (TITLE, SECTION_HEADER): navy, white text.
- Titles: 28 pt bold. Body placeholders: 18 pt (16 pt if over 300 characters) unless you set your own size.
- Every other text box keeps its size and bold; only font and colour are unified.
- Hard floor: nothing under 10 pt (case rule). Smaller text is raised to 10 pt.
- The intro slide (`intro_slide`) is skipped; edit `skip_slide_ids` to skip others.

How to use (ask Claude: "style the deck")
1. Claude reads the deck with this mask and saves it to JSON:
   revisionId,pageSize,layouts(objectId,layoutProperties.name),slides(objectId,slideProperties.layoutObjectId,pageElements(objectId,shape(shapeType,placeholder,text.textElements(textRun(content,style.fontSize,style.bold))),table(tableRows(tableCells(location,text.textElements.textRun.content)))))
2. `python3 style_deck.py deck.json --revision <revisionId> --dry-run`   (lists what will change)
3. Re-run without `--dry-run` and send the output to `update_presentation`.
The write is guarded by the revision id, so it fails safely if someone edits the deck mid-run.
Re-run any time after adding or pasting slides.

Known limits
- Google's connector has no tested way to edit the slide master, so styling is applied per slide. New slides
  you add later need one more run. (Tip: duplicate a styled slide instead of adding a blank one.)
- Images, charts and shapes you draw keep their own fills; only text and backgrounds are unified.
- It overrides text colours, including deliberate highlights. Say so if you want colour kept for a box.
