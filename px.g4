grammar px;

header_row
   : keyword '=' values ';' EOL
   ;

keyword
   : BASEKEY LANGUAGE? subkeys? ;

BASEKEY
   : [A-Z] [A-Z0-9\-]+ ;

LANGUAGE
   : '[' ( [a-z][a-z] ) ']' ;

subkeys
   : '(' quoted_string_list ')' ;

quoted_string_list
   : quoted_string ( ',' quoted_string )* ;

quoted_string
   : '"' NOT_QUOTE* '"' ;

values
   : integer
   | tlist_value
   | bare_string
   | hierarchy_levels
   | multiline_quoted_string_list
   ;

bare_string
   : NOT_STERM+
   ;

multiline_quoted_string
   : ( quoted_string EOL quoted_string ( EOL quoted_string )* )
   | quoted_string
   ;

multiline_quoted_string_list
   : multiline_quoted_string ( ',' EOL? multiline_quoted_string )* ;

tlist_value
   : 'TLIST(' TIME_SCALE ( ',' quoted_string '-' quoted_string )? ')'
          ( ',' EOL? multiline_quoted_string_list )? 
   ;

hierarchy_levels
   : quoted_string ',' quoted_string ':' quoted_string
     ( ',' EOL? quoted_string ':' quoted_string )*
   ;

integer
   : DIGITS
   ;

YEAR4
   : [0-9] [0-9] [0-9] [0-9]
   ;

TIME_SCALE
   : 'A1' 
   | 'H1' 
   | 'Q1' 
   | 'M1' 
   | 'W1'
   ;

EOL
   : '\r\n'
   | '\n'
   ;

NOT_QUOTE
   : ~["]
   ;

NOT_STERM
   : ~[";]
   ;


DIGITS
   : [0-9] +
   ;

STRING
   : ([a-zA-Z~0-9]) ([a-zA-Z0-9.+-])*
   ;
