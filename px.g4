grammar px;

@header {
package io.mikael.px;
}

px_file
    : header_row+
    ;

header_row
   : keyword '=' values ';' EOL
   ;

keyword
   : BASEKEY LANGUAGE? subkeys?
   ;

BASEKEY
   : [A-Z] [A-Z0-9\-]+
   ;

LANGUAGE
   : '[' ( [a-z][a-z] ) ']'
   ;

subkeys
   : '(' quoted_string_list ')'
   ;

quoted_string_list
   : QUOTED_STRING ( ',' QUOTED_STRING )*
   ;

values
   : integer
   | time_list
   | bare_string
   | hierarchy_levels
   | multiline_quoted_string_list
   ;

integer: (DIGITS)+ ;

bare_string
   : NOT_STERM+
   ;

multiline_quoted_string
   : sl+=QUOTED_STRING EOL sl+=QUOTED_STRING ( EOL sl+=QUOTED_STRING )*    # MultiLine
   | sl+=QUOTED_STRING                                                     # SingleLine
   ;

multiline_quoted_string_list
   : multiline_quoted_string ( ',' EOL? multiline_quoted_string )*
   ;

time_list
   : 'TLIST(' TIME_SCALE ( ',' QUOTED_STRING '-' QUOTED_STRING )? ')'
      ( ',' EOL? multiline_quoted_string_list )?
   ;

hierarchy_levels
   : QUOTED_STRING ',' QUOTED_STRING ':' QUOTED_STRING
     ( ',' EOL? QUOTED_STRING ':' QUOTED_STRING )*
   ;

TIME_SCALE
   : 'A1' 
   | 'H1' 
   | 'Q1' 
   | 'M1' 
   | 'W1'
   ;

QUOTED_STRING
   : '"' (~["])*? '"'
   ;

DIGITS
   : [0-9] +
   ;

EOL
   : '\r\n'
   | '\n'
   ;

QUOTE: ["] ;

SEMICOLON: [;] ;

NOT_STERM
   : ~[";]
   ;

