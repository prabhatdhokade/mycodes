/* SEARCH IN A ROW WISE AND COLUMN WISE SORTED MATRIX:

https://practice.geeksforgeeks.org/problems/search-in-a-matrix17201720/1#

Given an n x n matrix and a number x, find the position of x in the matrix 
if it is present in it. Otherwise, print “Not Found”. In the given matrix, 
every row and column is sorted in increasing order. 
The designed algorithm should have linear time complexity.
Example :

Input : mat[4][4] = { {10, 20, 30, 40},
                      {15, 25, 35, 45},
                      {27, 29, 37, 48},
                      {32, 33, 39, 50}};
              x = 29
Output : Found at (2, 1)

**** LOVELY QUESTION ****
*/

/*
#include <bits/stdc++.h>
using namespace std;

int main() {
    int n,m;
    cin>>n>>m;
    int arr[n][m];

    for(int i =0;i <n ;i++){
        for(int j=0;j<m;j++) {
            cin>>arr[i][j];
        }
    }
    int x;
    cin >> x;
    pair<int,int> p;
    p.first= -1;
    p.second= -1;

    int i =0;
    int j = m-1;

    while ( i>=0 && i<n && j>=0 && j<m ) {  // plz do dry run on paper you'll get to know the 
        // the logic,This is very LOVELY Question. 
        if ( arr[i][j] == x) {
            p.first= i;
            p.second= j;
            break;
        }   
        else if ( arr[i][j] > x) {
            j--;
        }
        else if ( arr[i][j] < x) {
            i++;
        }
    }

    cout<<p.first<< ","<<p.second; 
}
*/

#include<bits/stdc++.h>
using namespace std;

int solve(int n,int m,int arr[n][m],int k){  // dont know how to 
    int i=0;
    int j= m-1;
    while(i>=0 && i<n && j>=0 && j<m){
        if(arr[i][j] == k) return 1;
        else if(arr[i][j] > k) j--;
        else if(arr[i][j] < k) i++;
    }
    return 0;
}

int main(){
    int n;
    int m;
    cin>>n>>m;
    int arr[n][m];
    for(int i=0;i<n;i++){
        for(int j=0;j<m;j++){
            cin>>arr[i][j];
        }
    }
    int k;
    cin>>k;
    cout<<solve(n,m,arr,k);
}