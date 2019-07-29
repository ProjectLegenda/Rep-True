class Absnode():


# default action for node which needed to be transfered, all following interface should be re-defined for each implmentation of differernt model
    def __init__(self,node):
        self.node = node
        
    def getFpointer(self):
        return(self.node.fpointer) 
   
    def getBpointer(self):   
        return(self.node.bpointer)

    def getNodeSplitname(self):
        return('abs splitname')
 
    def getSplites(self):
        return(['abs splists'])
    
    def getCategory(self):
        return('abs category')
    



# concret class for node
class CHAID_to_vbanode(Absnode): 
 
    ## flater visit for node inforamtion  
 
    def __init__(self,node): 
 
        Absnode.__init__(self,node)
        # by using a intermediate transformation of a node to get attriute easily 
 
    def getNodeSplitname(self): 
        return(self.node.tag.split.split_name + '.value')     
     
    def getSplits(self): 
        return([i.__str__().replace('[','').replace(']','') for i in self.node.tag.split.splits]) 
     
    def getCategory(self): 
        members = self.node.tag.members 
        max_key = max(members,key = members.get) 
        return( 'y= ' + str(max_key)) 


class CHAID_to_sqlnode(Absnode):
     
    def __init__(self,node):
        Absnode.__init__(self,node)

    def getNodeSplitname(self):
        return(self.node.tag.split.split_name )

    def getSplits(self):
        return([i.__str__().replace('[','(').replace(']',')') for i in self.node.tag.split.splits])

    def getCategory(self):
        members = self.node.tag.members
        max_key = max(members,key = members.get)
        return(str(max_key))





