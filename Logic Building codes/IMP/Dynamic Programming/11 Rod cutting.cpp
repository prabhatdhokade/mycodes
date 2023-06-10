/* 
Exact unbounded question 

Rod Cutting Problem
 Given a rod of length n inches and an array of prices that contains prices of all pieces of size smaller than n. 
 Determine the  maximum value obtainable by cutting up the rod and selling the pieces. 
Example: 
if length of the rod is 8 and the values of different pieces are given as following, then the maximum obtainable 
value is 22 (by cutting in two pieces of lengths 2 and 6)


length   | 1   2   3   4   5   6   7   8  
--------------------------------------------
price    | 1   5   8   9  10  17  17  20

output : 22 */
#include<bits/stdc++.h>

using namespace std;
 
int solve(int length[],int price[],int n,int N){

    int t[n+1][N+1];      // we can make this as t[size.length()+1] [N+1]
    for(int i =0;i<n+1;i++){
        for(int j=0;j<N+1;j++){
            if(i==0 || j==0){
                t[i][j] = 0;
            }
        }
    }

    for(int i=1;i<n+1;i++){
        for(int j=1;j<N+1;j++){
            if(length[i-1] <= j){

                t[i][j] =max(price[i-1] + t[i] [j-length[i-1]] , t[i-1][j]); 
                 // this is is the exacct same question as the unbounded knapsack 
            }
            else 
                t[i][j] = t[i-1][j];
        }
    }

    return t[n][N];
}


int main() {
    int n;
    cin>>n;
    int N;
    cin>>N;
    int length[n];
    for(int i =0;i<n;i++){
        length[i] = i+1;
    }
    int price[n];
    for(int i =0;i<n;i++){
        cin>>price[i];
    }
    cout<<solve(length,price,n,N);
}