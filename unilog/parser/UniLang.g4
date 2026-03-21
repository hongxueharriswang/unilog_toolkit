
grammar UniLang;
@header { package unilog.parser; }
// Lexer
ID:[A-Za-z_][A-Za-z0-9_]*; INT:[0-9]+; REAL:[0-9]+('.'[0-9]+)?; STRING:'"'( ~["\\] | '\\' . )* '"';
COMMENT:('//' ~[\r\n]* | '%' ~[\r\n]*)->skip; WS:[ \t\r\n]+->skip;
AND:'and'; OR:'or'; NOT:'not'; IMPL:'->'; IFF:'<->'; FORALL:'forall'; EXISTS:'exists'; TRUE:'true'; FALSE:'false';
BOX:'box'; DIAM:'diamond'; KMOD:'K'; BMOD:'B'; OMOD:'O'; PMOD:'P'; GLOB:'G'; FUT:'F'; NEXT:'X'; UNTIL:'U'; RELEASE:'R';
ACTTEST:'?'; OPT:'Opt'; PROB_GE:'P_>='; PROB_LE:'P_<='; PROB_EQ:'P_='; EXPECT:'E';
FU_AND_G:'&G'; FU_AND_L:'&L'; FU_AND_P:'&P'; FU_OR_G:'|G'; FU_OR_L:'|L'; FU_OR_P:'|P'; FU_NOT_G:'~G'; FU_NOT_L:'~L'; FU_NOT_P:'~P'; GRADE_GE:'T_>=';
DEFIMPL:'=>'; PREF:'<'; LBRACK:'['; RBRACK:']'; LANGLE:'<'; RANGLE:'>'; LPAREN:'('; RPAREN:')'; LBRACE:'{'; RBRACE:'}'; COMMA:','; DOT:'.'; COLON:':'; SEMI:';'; ASSIGN:'='; NEQ:'!='; STAR:'*'; SEMI_ACT:';'; CHOICE:'|';
// Parser
start:(signature)? formula* EOF; signature:'signature' LBRACE decl* RBRACE; decl:sortDecl|constDecl|funDecl|predDecl|actionDecl; sortDecl:'sort' ID (COMMA ID)* SEMI; constDecl:'constant' ID COLON ID SEMI; funDecl:'function' ID LPAREN (typedId (COMMA typedId)*)? RPAREN COLON ID SEMI; predDecl:'predicate' ID LPAREN (typedId (COMMA typedId)*)? RPAREN SEMI; actionDecl:'action' ID LPAREN (typedId (COMMA typedId)*)? RPAREN? SEMI?; typedId:ID (COLON ID)?;
term:ID (LPAREN term (COMMA term)* RPAREN)? | STRING | INT | REAL; interval:'_[' REAL COMMA REAL ']';
formula:prefExpr; prefExpr:implExpr (PREF implExpr)?; implExpr:iffExpr (DEFIMPL iffExpr | IMPL iffExpr)?; iffExpr:orExpr (IFF orExpr)*; orExpr:andExpr ((OR|FU_OR_G|FU_OR_L|FU_OR_P) andExpr)*; andExpr:untilExpr ((AND|FU_AND_G|FU_AND_L|FU_AND_P) untilExpr)*; untilExpr:unaryExpr ((UNTIL interval? | RELEASE interval?) unaryExpr)?;
unaryExpr: NOT unaryExpr | FU_NOT_G unaryExpr | FU_NOT_L unaryExpr | FU_NOT_P unaryExpr | FORALL ID (COLON ID)? DOT unaryExpr | EXISTS ID (COLON ID)? DOT unaryExpr | BOX (LBRACK ID RBRACK)? unaryExpr | DIAM (LBRACK ID RBRACK)? unaryExpr | KMOD LBRACK ID RBRACK unaryExpr | BMOD LBRACK ID RBRACK unaryExpr | OMOD unaryExpr | PMOD unaryExpr | GLOB (interval)? unaryExpr | FUT (interval)? unaryExpr | NEXT unaryExpr | LBRACK action RBRACK unaryExpr | LANGLE action RANGLE unaryExpr | PROB_GE REAL LPAREN formula RPAREN | PROB_LE REAL LPAREN formula RPAREN | PROB_EQ REAL LPAREN formula RPAREN | EXPECT LBRACK term RBRACK | OPT LPAREN formula RPAREN | concept LPAREN term RPAREN | atom | TRUE | FALSE | LPAREN formula RPAREN;
action: ID | action SEMI_ACT action #actSeq | action CHOICE action #actChoice | action STAR #actStar | ACTTEST formula #actTest | LPAREN action RPAREN #actParen;
concept: ID | 'and' LPAREN concept (COMMA concept)* RPAREN | 'or' LPAREN concept (COMMA concept)* RPAREN | 'not' LPAREN concept RPAREN | 'some' ID concept | 'all' ID concept | 'atleast' INT ID concept | 'atmost' INT ID concept;
atom: ID LPAREN term (COMMA term)* RPAREN | term ASSIGN term | term NEQ term;
