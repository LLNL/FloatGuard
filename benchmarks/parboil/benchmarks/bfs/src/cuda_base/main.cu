/***********************************************************************************
  Implementing Breadth first search on CUDA using algorithm given in DAC'10
  paper "An Effective GPU Implementation of Breadth-First Search"

  Copyright (c) 2010 University of Illinois at Urbana-Champaign. 
  All rights reserved.

  Permission to use, copy, modify and distribute this software and its documentation for 
  educational purpose is hereby granted without fee, provided that the above copyright 
  notice and this permission notice appear in all copies of this software and that you do 
  not sell the software.

  THE SOFTWARE IS PROVIDED "AS IS" AND WITHOUT WARRANTY OF ANY KIND,EXPRESS, IMPLIED OR 
  OTHERWISE.

  Author: Lijiuan Luo (lluo3@uiuc.edu)
  Revised for Parboil 2 Benchmark Suite by: Geng Daniel Liu (gengliu2@illinois.edu)
 ************************************************************************************/
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <parboil.h>
#include <deque>
#include <iostream>

#include "config.h"
FILE *fp;

typedef int2 Node;
typedef int2 Edge;

#include "kernel.cu"
//Somehow "hipMemset" does not work. So I use hipMemcpy of constant variables for initialization
const int h_top = 1;
const int zero = 0;

////////////////////////////////////////////////////////////////////////////////
// Main Program
////////////////////////////////////////////////////////////////////////////////
int main(int argc, char** argv) 
{
  //the number of nodes in the graph
  int num_of_nodes = 0; 
  //the number of edges in the graph
  int num_of_edges = 0;
  struct pb_Parameters *params;
  struct pb_TimerSet timers;

  pb_InitializeTimerSet(&timers);
  params = pb_ReadParameters(&argc, argv);
  if ((params->inpFiles[0] == NULL) || (params->inpFiles[1] != NULL))
  {
    fprintf(stderr, "Expecting one input filename\n");
    exit(-1);
  }

  pb_SwitchToTimer(&timers, pb_TimerID_IO);
  //printf("Reading File\n");
  //Read in Graph from a file
  fp = fopen(params->inpFiles[0],"r");
  if(!fp)
  {
    printf("Error Reading graph file\n");
    return 0;
  }
  int source;

  fscanf(fp,"%d",&num_of_nodes);
  // allocate host memory
  Node* h_graph_nodes = (Node*) malloc(sizeof(Node)*num_of_nodes);
  int *color = (int*) malloc(sizeof(int)*num_of_nodes);
  int start, edgeno;   
  // initalize the memory
  for( unsigned int i = 0; i < num_of_nodes; i++) 
  {
    fscanf(fp,"%d %d",&start,&edgeno);
    h_graph_nodes[i].x = start;
    h_graph_nodes[i].y = edgeno;
    color[i]=WHITE;
  }
  //read the source node from the file
  fscanf(fp,"%d",&source);
  fscanf(fp,"%d",&num_of_edges);
  int id,cost;
  Edge* h_graph_edges = (Edge*) malloc(sizeof(Edge)*num_of_edges);
  for(int i=0; i < num_of_edges ; i++)
  {
    fscanf(fp,"%d",&id);
    fscanf(fp,"%d",&cost);
    h_graph_edges[i].x = id;
    h_graph_edges[i].y = cost;
  }
  if(fp)
    fclose(fp);    

  // allocate mem for the result on host side
  int* h_cost = (int*) malloc( sizeof(int)*num_of_nodes);
  for(int i = 0; i < num_of_nodes; i++){
    h_cost[i] = INF;
  }
  h_cost[source] = 0;

  pb_SwitchToTimer(&timers, pb_TimerID_COPY);

  //Copy the Node list to device memory
  Node* d_graph_nodes;
  hipMalloc((void**) &d_graph_nodes, sizeof(Node)*num_of_nodes);
  hipMemcpy(d_graph_nodes, h_graph_nodes, sizeof(Node)*num_of_nodes, hipMemcpyHostToDevice);
  //Copy the Edge List to device Memory
  Edge* d_graph_edges;
  hipMalloc((void**) &d_graph_edges, sizeof(Edge)*num_of_edges);
  hipMemcpy(d_graph_edges, h_graph_edges, sizeof(Edge)*num_of_edges, hipMemcpyHostToDevice);

  int* d_color;
  hipMalloc((void**) &d_color, sizeof(int)*num_of_nodes);
  int* d_cost;
  hipMalloc((void**) &d_cost, sizeof(int)*num_of_nodes);
  int * d_q1;
  int * d_q2;
  hipMalloc( (void**) &d_q1, sizeof(int)*num_of_nodes);
  hipMalloc( (void**) &d_q2, sizeof(int)*num_of_nodes);
  int * tail;
  hipMalloc( (void**) &tail, sizeof(int));
  int *front_cost_d;
  hipMalloc( (void**) &front_cost_d, sizeof(int));
  hipMemcpy( d_color, color, sizeof(int)*num_of_nodes, hipMemcpyHostToDevice);
  hipMemcpy( d_cost, h_cost, sizeof(int)*num_of_nodes, hipMemcpyHostToDevice);

  //bind the texture memory with global memory
  hipBindTexture(0,g_graph_node_ref,d_graph_nodes, sizeof(Node)*num_of_nodes);
  hipBindTexture(0,g_graph_edge_ref,d_graph_edges,sizeof(Edge)*num_of_edges);

  printf("Starting GPU kernel\n");
  (hipDeviceSynchronize());
  pb_SwitchToTimer(&timers, pb_TimerID_KERNEL);
  
  int num_of_blocks; 
  int num_of_threads_per_block;

  hipMemcpy(tail,&h_top,sizeof(int),hipMemcpyHostToDevice);
  hipMemcpy(&d_cost[source],&zero,sizeof(int),hipMemcpyHostToDevice);

  hipMemcpy( &d_q1[0], &source, sizeof(int), hipMemcpyHostToDevice);
  int num_t;//number of threads
  int k=0;//BFS level index

  do
  {
    (hipMemcpy(&num_t, tail, sizeof(int), hipMemcpyDeviceToHost) );
    (hipMemcpy(tail,&zero,sizeof(int),hipMemcpyHostToDevice));

    if(num_t == 0){//frontier is empty
      break;
    }

    num_of_blocks = 1;
    num_of_threads_per_block = num_t;
    if(num_of_threads_per_block <NUM_BIN)
      num_of_threads_per_block = NUM_BIN;
    if(num_t>MAX_THREADS_PER_BLOCK)
    {
      num_of_blocks = (int)ceil(num_t/(double)MAX_THREADS_PER_BLOCK); 
      num_of_threads_per_block = MAX_THREADS_PER_BLOCK;
    }
    if(num_of_blocks == 1)//will call "BFS_in_GPU_kernel" 
      num_of_threads_per_block = MAX_THREADS_PER_BLOCK; 
    if(num_of_blocks >1 && num_of_blocks <= NUM_SM)// will call "BFS_kernel_multi_blk_inGPU"
      num_of_blocks = NUM_SM;

    dim3  grid( num_of_blocks, 1, 1);
    dim3  threads( num_of_threads_per_block, 1, 1);

    if(k%2 == 0){
      BFS_kernel<<< grid, threads >>>(d_q1,d_q2, d_graph_nodes, 
          d_graph_edges, d_color, d_cost, num_t, tail,GRAY0,k);
    }
    else{
      BFS_kernel<<< grid, threads >>>(d_q2,d_q1, d_graph_nodes, 
          d_graph_edges, d_color, d_cost, num_t, tail, GRAY1,k);
    }
    k++;
  }
  while(1);
  hipDeviceSynchronize();
  pb_SwitchToTimer(&timers, pb_TimerID_COPY);
  printf("GPU kernel done\n");

  // copy result from device to host
  hipMemcpy(h_cost, d_cost, sizeof(int)*num_of_nodes, hipMemcpyDeviceToHost);
  hipMemcpy(color, d_color, sizeof(int)*num_of_nodes, hipMemcpyDeviceToHost);
  hipUnbindTexture(g_graph_node_ref);
  hipUnbindTexture(g_graph_edge_ref);

  hipFree(d_graph_nodes);
  hipFree(d_graph_edges);
  hipFree(d_color);
  hipFree(d_cost);
  hipFree(tail);
  hipFree(front_cost_d);
  //Store the result into a file
  pb_SwitchToTimer(&timers, pb_TimerID_IO);
  FILE *fp = fopen(params->outFile,"w");
  fprintf(fp, "%d\n", num_of_nodes);
  for(int i=0;i<num_of_nodes;i++)
    fprintf(fp,"%d %d\n",i,h_cost[i]);
  fclose(fp);

  // cleanup memory
  free( h_graph_nodes);
  free( h_graph_edges);
  free( color);
  free( h_cost);
  pb_SwitchToTimer(&timers, pb_TimerID_NONE);
  pb_PrintTimerSet(&timers);
  pb_FreeParameters(params);
  return 0;
}
