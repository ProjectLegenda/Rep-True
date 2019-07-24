from treelib.tree import Tree

from treelib.node import Node

class Std_node():


    ## flater visit for node inforamtion 

    def __init__(self,node):

        # by using a intermediate transformation of a node to get attriute easily

        self.node = node
        
        self.fpointer = node.fpointer

        self.bpointer = node.bpointer

        self.split_name = node.tag.split.split_name

        self.splits = node.tag.split.splits
    
        self.members = node.tag.members

    def get_original_node(self):
        return(self.node)
    
    def get_category(self):
        max_key = max(self.members,key = self.members.get)
        return(max_key)


class Tree_transverser():
    
     def __init__(self,tree,indent_char = ' '*4,symbol = 'case', when = 'when', then = 'then', end = 'end'):


         self.tree = tree
         self.indent = 1 
         self.final_str = ''

         self.indent_char = indent_char

         self.symbol = symbol
         self.when = when
         self.then = then
         self.end = end

         self.transversal()
         print(self.__str__())    
      
     def eval_node(self,nid):
      
         self.indent = self.indent + 1
         current_node = Std_node(self.tree.get_node(nid))
         
         length = len(current_node.fpointer)

         if length != 0:

             for i,child_nid in enumerate(current_node.fpointer):

                 if i == 0: 
                     self.final_str = self.final_str + str(self.indent * self.indent_char)\
                         +  self.symbol + '\n'

                 self.final_str = self.final_str + str(self.indent * self.indent_char)\
                     + self.when + ' '\
                     + current_node.split_name\
                     + ' in '\
                     + current_node.splits[i].__str__().replace('[','(').replace(']',')')\
                     + ' ' + self.then + ' \n'

                 self.eval_node(child_nid)
             
             self.final_str = self.final_str + str(self.indent * self.indent_char)  + self.end + ' \n'

         else:
       
             self.final_str = self.final_str + str(self.indent * self.indent_char) + str(current_node.get_category()) + '\n'

         self.indent = self.indent - 1
 
     def transversal(self):
         self.eval_node(self.tree.root)       
      
     def __str__(self):
         return(self.final_str)


if __name__ == '__main__':  

    from chaid_v2 import tree
    t = tree.to_tree()

    trans = Tree_transverser(t,symbol = 'case', when = 'when',then = 'then',end = 'end') 

    pass

