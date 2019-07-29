#define target language syntax objects 

    
class vbaSyntax():

    STARTWITH = 'select'
    SWITCH = 'case'
    THEN = ''
    IN_CLAUSE = 'case'       
    END= 'end select'
        
    
class sqlSyntax():

    STARTWITH='case'
    SWITCH = 'when'
    THEN ='then'
    IN_CLAUSE = 'in'
    END = 'end'
