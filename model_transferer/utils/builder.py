from model_transferer.utils.tree_transverser import Tree_transverser
from model_transferer.utils.syntax import vbaSyntax
from model_transferer.utils.syntax import sqlSyntax
from model_transferer.utils.node import CHAID_to_vbanode 
from model_transferer.utils.node import CHAID_to_sqlnode 


class transferer_builder():

    def __init__(self):
        self.tree_transverser = Tree_transverser()

    def buildNodeFactory(self,node_typ):

        if node_typ == 'CHAIDtovba':
            self.tree_transverser.bindNodeFactory(CHAID_to_vbanode)
 
        if node_typ == 'CHAIDtosql':
            self.tree_transverser.bindNodeFactory(CHAID_to_sqlnode)

    def getTransverser(self):
        return(self.tree_transverser)
    

