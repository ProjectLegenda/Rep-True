package com.iqvia.aa;

import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
//import org.apache.solr.client.solrj.response.UpdateResponse;
import org.apache.solr.common.SolrDocument;
import org.apache.solr.common.SolrDocumentList;
//import org.apache.solr.common.SolrInputDocument;
//import org.apache.solr.common.params.MapSolrParams;

import org.apache.solr.common.params.SolrParams;

//import iqvia.solrWrappedParams; 

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class solrWrappedClient{

    private String core;

    private HttpSolrClient client;

    private SolrParams queryParams;

    public void setQueryParams(String searchstr,String start,String rows){

    solrWrappedParams wrappedparames = new solrWrappedParams();
    this.queryParams = wrappedparames.getParams(searchstr,start,rows);

   }

    public void setSolrClient(String BaseUrl){

        /*
         * 设置超时时间
         * .withConnectionTimeout(10000)
         * .withSocketTimeout(60000)
         */
        this.client = new HttpSolrClient.Builder(BaseUrl)
                .withConnectionTimeout(10000)
                .withSocketTimeout(60000)
                .build();
    }

    public void setCore(String core){

        this.core = core;

    }
   
    public QueryResponse Query(String searchstr) throws IOException, SolrServerException {
        
        this.setQueryParams(searchstr,"0","300");

        QueryResponse response = this.client.query(this.core,this.queryParams);
        // 获取结果集
        return(response);
    }

  
    //overwriteen method
    public QueryResponse Query(String searchstr, String start,String rows) throws IOException, SolrServerException {
        
        this.setQueryParams(searchstr,start,rows);

        QueryResponse response = this.client.query(this.core,this.queryParams);
        // 获取结果集
        return(response);
    }

    public void close() throws IOException{
     //delegate of original client
        this.client.close();


    }    
    
    public HttpSolrClient getSolrClient(){
    
   //TODO null exception handle
        return this.client;

    }
}
