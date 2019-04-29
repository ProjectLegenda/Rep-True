package com.iqvia.aa;

import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrInputDocument;
import org.apache.solr.common.params.MapSolrParams;
import org.apache.solr.common.params.SolrParams;
//import org.junit.Test;
 
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class solrWrappedParams{

    private MapSolrParams WrappedParams;
   
    private SolrParams Params; 

    public void solrWrappedParams(){

    }

    protected void setParams(String searchString, String start, String rows ){

        Map<String, String> params = new HashMap<String, String>();
    
        //query field
        params.put("q","collector" + ":" + searchString);
        //high light
        params.put("hl","true");
        
        params.put("hl.fl","title,context,reference");
    
        params.put("start",start);
   
        params.put("rows",rows);
        //DEbug
        //Map parameters
        this.Params = new MapSolrParams(params);

    }

    //no pagnating

    public SolrParams getParams(String searchString,String start,String rows){
        this.setParams(searchString,start,rows);
        return(this.Params);

    }
}  
    
