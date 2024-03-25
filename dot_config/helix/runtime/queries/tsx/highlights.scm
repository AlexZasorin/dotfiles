(jsx_opening_element ["<" ">"] @attribute.bracket)
(jsx_closing_element ["</" ">"] @attribute.bracket)
(jsx_self_closing_element ["<" "/>"] @attribute.bracket)

(import_specifier (identifier) @mycapture)

; inherits: _jsx,_typescript,ecma
