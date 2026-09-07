.. raw:: pdf

   PageBreak recipePage

.. HTML page break intentionally removed. In the epub/HTML build the page
   break is applied via CSS on the recipe heading (h3) in assets/Cookbook.css,
   so the break coincides with the heading's anchor. The old standalone
   `<p style="page-break-before: always">` here became a trailing sibling of
   the previous recipe and caused Kobo TOC links to land on the previous
   recipe's last page. The PDF build still breaks via the `.. raw:: pdf` block
   above.
