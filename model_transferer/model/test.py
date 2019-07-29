from chaid import tree
from model_transferer.utils.builder import transferer_builder  

builder = transferer_builder()

builder.buildSyntax('sql')
builder.buildNodeFactory('CHAIDtosql')

trans = builder.getTransverser()


t = tree.to_tree()

trans.bindTree(t)

trans.transverse()


builder.buildSyntax('vba')
builder.buildNodeFactory('CHAIDtovba')

trans = builder.getTransverser()

trans.transverse()




