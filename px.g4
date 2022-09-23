grammar px;

header_row
   : keyword '=' values ';' EOL ;

keyword
   : BASEKEY LANGUAGE? subkeys? ;

BASEKEY
   : ( [A-Z] ) ( [A-Z0-9\-] )* ;

LANGUAGE
   : '[' ( [a-z][a-z] ) ']' ;

subkeys
   : '(' quoted_string_list ')' ;

quoted_string_list
   : quoted_string { "," quoted_string } ;

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
   : { all characters - ( ";" | '"' ) }+ ;

multiline_quoted_string
   : ( quoted_string EOL quoted_string { EOL quoted_string } )
   | quoted_string
   ;

quoted_string_list
   : quoted_string { "," quoted_string }
   ;

multiline_quoted_string_list
   : multiline_quoted_string { "," EOL? multiline_quoted_string } ;




NOT_QUOTE
   : [^"];


string
   : STRING
   | DIGITS
   ;


DIGITS
   : [0-9] +
   ;


STRING
   : ([a-zA-Z~0-9]) ([a-zA-Z0-9.+-])*
   ;


/*
url
   : uri EOF
   ;

uri
   : scheme '://' login? host (':' port)? ('/' path?)? query? frag? WS?
   ;

scheme
   : string
   ;

host
   : '/'? hostname
   ;

hostname
   : string ('.' string)*   #DomainNameOrIPv4Host
   | '[' v6host ']'         #IPv6Host
   ;

v6host
   : '::'? (string | DIGITS) ((':'|'::') (string | DIGITS))*
   ;

port
   : DIGITS
   ;

path
   : string ('/' string)* '/'?
   ;

user
   : string
   ;

login
   : user (':' password)? '@'
   ;

password
   : string
   ;

frag
   : '#' (string | DIGITS)
   ;

query
   : '?' search
   ;

search
   : searchparameter ('&' searchparameter)*
   ;

searchparameter
   : string ('=' (string | DIGITS | HEX))?
   ;

string
   : STRING
   | DIGITS
   ;


DIGITS
   : [0-9] +
   ;


HEX
   : ('%' [a-fA-F0-9] [a-fA-F0-9]) +
   ;


STRING
   : ([a-zA-Z~0-9] | HEX) ([a-zA-Z0-9.+-] | HEX)*
   ;


WS
   : [\r\n] +
   ;
*/
