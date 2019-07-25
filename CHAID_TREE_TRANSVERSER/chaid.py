import pandas as pd

#pip3 install CHAID
import CHAID
from CHAID import Tree

#=====================================
# data

df = pd.read_csv('data.csv')
df

features = ['Q1_1',
   'Q1_2',
   'Q1_3',
   'Q1_4',
   'Q1_5',
   'Q1_6',
   'Q1_7',
   'Q1_8',
   'Q1_9',
   'Q1_10',
   'Q1_11',
   'Q1_12',
   'Q1_13',
   'Q1_14',
   'Q2_1',
   'Q2_2',
   'Q2_3',
   'Q2_4',
   'Q2_5',
   'Q2_6',
   'Q2_7',
   'Q2_8',
   'Q2_9',
   'Q2_10',
   'Q3_1',
   'Q3_2',
   'Q3_3',
   'Q3_4',
   'Q3_5',
   'Q3_6',
   'Q3_7',
   'Q3_8',
   'Q3_9',
   'Q3_10']

len(features)

#=====================================
# create tree

features
dict(zip(features, ['ordinal'] * 34))
     
tree = Tree.from_pandas_df(df, 
                           dict(zip(features, ['ordinal'] * 34)), 
                           'clus', 
                           dep_variable_type='categorical',
                           alpha_merge=0.05,
                           max_depth=2,
                           min_parent_node_size=1,
                           min_child_node_size=0, 
                           split_threshold=0)

tree

tree.print_tree() 

dir(tree)

dir(tree.get_node(3))
tree.get_node(0)._members








