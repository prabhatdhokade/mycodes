/* Subset Sum Problem(Dynamic Programming)
Given a set of non-negative integers, and a value sum, 
determine if there is a subset of the given set with sum equal to given sum.
Example:

Input:  set[] = {3, 34, 4, 12, 5, 2}, sum = 9
Output:  True  //There is a subset (4, 5) with sum 9.*/


#include<bits/stdc++.h>
using namespace std;

bool solve(int arr[],int n,int W){
    bool t[n+1][W+1];

    for(int i =0;i<n+1;i++) {   //for every 'n' we put 'i'
        for(int j =0; j<W+1; j++) { // for every 'W' we put 'j'
            
            if( i == 0) {
                t[i][j] = false;
            }
            if ( j == 0) {
                t[i][j] = true;
            }
        }
    }

    for(int i =1; i<n+1;i++) {
        for(int j=1;j<W+1;j++) {
            if(arr[i-1] <= j) {
                t[i][j] = t[i-1][j-arr[i-1]] || t[i-1][j]; //this or operator will return whichever the statement returns true value it will take that; //here we use or operator to eihter we 
            }                                  // want to add it in the subset or leave it
            else if(arr[i-1] > j) {
                t[i][j] = t[i-1][j];
            }
        }
    }
    for(int j=0;j<W;j++){
        if(t[n][j] == true) {
            cout<<j<<" ";
        }
    }

    return t[n][W];

}

int main() 
{
    int n;
    cin >> n;
    int W;
    cin >> W; // W indicates sum
    int arr[n];
    for(int i =0;i<n;i++) {
        cin>>arr[i];
    }

    cout<<solve(arr,n,W);

}