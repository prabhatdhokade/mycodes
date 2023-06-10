/* 0-1 Knapsack Problem solution using Memoization.
Knapsack Memoization code requires only 4 changes in Knapsack Recursion code.*/


#include<bits/stdc++.h>

using namespace std;

int static t[100][100];// initialize it globaly

int solve(int val[],int wt[],int W,int n) {
    if(n == 0 || W == 0) {
        return 0;
    }
    if(t[n][W]!= -1) {   // this is called memoization
        return t[n][W]; // if the value is present already then we'll return it from here only
    }
    if(wt[n-1] <= W) {
        return t[n][W] = max(val[n-1] + solve(val,wt,W-wt[n-1],n-1),solve(val,wt,W,n-1)); //we want the 
        // sum maximum values we can store it into the knapsack  
        // we'll save the value into matrix for reducing the next recursion
    }
    else if(wt[n-1] > W) {
        return t[n][W] = solve(val,wt,W,n-1);
    }
    return -1;
}
  
int main() 
{
    int n;
    cin>> n;
    int W;
    cin>>W;
    int val[n];
    int wt[n];
    for(int i=0;i<n;i++) {
        cin>>val[i];
    }
    for(int i =0;i<n;i++) {
        cin>>wt[i];
    }
    memset(t,-1,sizeof(t));
    cout<< solve(val,wt,W,n);
}