/* 0-1 Knapsack Problem solution using recursion(Overlapping Subproblems).

Example:
 Given weights and values of n items, put these items in a knapsack of capacity W to 
 get the maximum total value in the knapsack. In other words, given two integer arrays 
 val[0..n-1] and wt[0..n-1] which represent values and weights associated with n items 
 respectively. Also given an integer W which represents knapsack capacity, find out the 
 maximum value subset of val[] such that sum of the weights of this subset is smaller 
 than or equal to W. You cannot break an item, either pick the complete item, or don’t 
 pick it (0-1 property).
input :3
  3
  1 2 3
  4 5 6
output : 3
 */


#include<bits/stdc++.h>

using namespace std;

int solve(int val[],int wt[],int W,int n) {
    if(n == 0 || W == 0) {  // when the weight or number  of items becomes 0, we return 0
        return 0;
    }
    if(wt[n-1] <= W) {
        return max(val[n-1] + solve(val,wt,W-wt[n-1],n-1),solve(val,wt,W,n-1)); //we want the 
        // sum maximum values we can store it into the knapsack  
    }
    else if(wt[n-1] > W) {
        return solve(val,wt,W,n-1);
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
    cout<< solve(val,wt,W,n);
}