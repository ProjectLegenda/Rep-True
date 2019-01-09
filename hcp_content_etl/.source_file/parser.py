from html.parser import HTMLParser

class SimpleHTMLparser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.final_data = ''

    def handle_data(self,data):
        """
        cumulative data from source,replace semi comma to full comma

        """
        self.final_data = self.final_data.replace(',','，').replace('\n','') + data

    def getdata(self):
        t = self.final_data
        self.final_data = ''
        return(t)



