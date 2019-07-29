from chaid import tree
from model_transferer.utils.sdt import Tree_transverser  

t = tree.to_tree()

trs = Tree_transverser()

trs.bind_tree(t)

trs.transverse()





