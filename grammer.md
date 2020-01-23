# Implemented

```
body         : (prop_section | text_section)*

text_section : (text_line | text_comment | tag | text_heading )* text_par_end
text_line    : (alphanummore) NEWLINE
text_par_end : NEWLINE
text_comment : ! .* NEWLINE
text_heading : (heading_1 | heading_2 | heading_3)
text_list    : list_level_1 | list_level_2 | list_level_3

heading_1    : HASH alphanummore
heading_2    : HASH HASH alphanummore
heading_3    : HASH HASH HASH alphanummore

list_level_1 : MINUS alphanummore NEWLINE
list_level_2 : IDENT MINUS alphanummore NEWLINE
list_level_3 : IDENT IDENT MINUS alphanummore NEWLINE

alphanum     : (TEXT | NUM | UNDERSCORE | EXCLAIM | MINUS )*
alphanummore : (TEXT | NUM | COLON)*
tag          : LTAG (TEXT | NUM)* [COLON alphanum*] RTAG NEWLINE

prop_section : prop_div (prop_line)* prop_div 
prop_div     : MINUS MINUS MINUS 
prop_line    : [[[EXCLAIM]TEXT BAR]TEXT COLON TEXT]NEWLINE
```

# todo

```
```
