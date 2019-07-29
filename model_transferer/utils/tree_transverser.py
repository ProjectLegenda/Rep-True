#core of tree transverser

class Tree_transverser():
    
     def __init__(self):

         self.indent = 1 
         self.final_str = ''
         self.indent_char = ' '*4 

     def bindTree(self,tree):
         self.tree = tree


     def bindSyntax(self,syntax):

         self.startwith = syntax.STARTWITH
         self.switch = syntax.SWITCH
         self.in_clause = syntax.IN_CLAUSE
         self.then = syntax.THEN
         self.end = syntax.END
         
              
     def bindNodeFactory(self,node_factory):
         self.node_factory = node_factory
          
     def eval_node(self,nid):
      
         self.indent = self.indent + 1
         current_node = self.node_factory(self.tree.get_node(nid))
         
         length = len(current_node.getFpointer())

         if length != 0:

             for i,child_nid in enumerate(current_node.getFpointer()):

                 if i == 0: 
                     self.final_str = self.final_str + str(self.indent * self.indent_char)\
                         +  self.startwith + '\n'

                 self.final_str = self.final_str + str(self.indent * self.indent_char)\
                     + self.switch + ' '\
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





