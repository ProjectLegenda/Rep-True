from model_transferer.utils.nodes import Transformed_CHAID_node

class Tree_transverser():
    
     def __init__(self,indent_char = ' '*4,symbol = 'case ', when = 'when', then = 'then', in_clause = 'in', end = 'end',node_factory = Transformed_CHAID_node):

         self.indent = 1 
         self.final_str = ''

         self.node_factory = node_factory
         self.indent_char = indent_char

         self.symbol = symbol
         self.when = when
         self.then = then
         self.end = end
         self.in_clause = in_clause

         #self.transversal()
         #print(self.__str__())    
      
     def bind_tree(self,tree):
         self.tree = tree


     def eval_node(self,nid):
      
         self.indent = self.indent + 1
         current_node = self.node_factory(self.tree.get_node(nid))
         
         length = len(current_node.getFpointer())

         if length != 0:

             for i,child_nid in enumerate(current_node.getFpointer()):

                 if i == 0: 
                     self.final_str = self.final_str + str(self.indent * self.indent_char)\
                         +  self.symbol + '\n'

                 self.final_str = self.final_str + str(self.indent * self.indent_char)\
                     + self.when + ' '\
                     + current_node.getNodeSplitname()\
                     + ' {} '.format(self.in_clause)\
                     + current_node.getSplits()[i]\
                     + ' ' + self.then + ' \n'

                 self.eval_node(child_nid)
             
             self.final_str = self.final_str + str(self.indent * self.indent_char)  + self.end + ' \n'

         else:
       
             self.final_str = self.final_str + str(self.indent * self.indent_char) + str(current_node.getCategory()) + '\n'

         self.indent = self.indent - 1
 
     def transverse(self):
         self.eval_node(self.tree.root)       
         print(self.final_str)
      
     def __str__(self):
         return(self.final_str)





