/*Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it is able to trap after raining.
Input: arr[]   = {2, 0, 2}
Output: 2
Structure is like below
| |
|_|
We can trap 2 units of water in the middle gap.

Input: arr[]   = {3, 0, 0, 2, 0, 4}
Output: 10
Structure is like below
     |
|    |
|  | |
|__|_| 
We can trap "3*2 units" of water between 3 an 2,
"1 unit" on top of bar 2 and "3 units" between 2 
and 4.  See below diagram also.
 input : 6
         3 0 0 2 0 4
 output : 10        
 */

#include<bits/stdc++.h>

using namespace std ;

/*
int main() 
{ 
    int n ;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++) {
        cin>>arr[i];
    }

    int mxl[n];   
    mxl[0] = arr[0];  // mxl =maximum left  
    for ( int i =1 ; i < n ; i++) {
        mxl[i] = max(mxl[i-1] ,arr[i]); // select the maximum of left off each element
    } // mxl = 3 3 3 3 3 4
    int mxr[n];
    mxr[n-1] = arr[n-1]; // mxr = maximum of right
    for ( int i = n-2 ; i>=0 ; i--) { 
        mxr[i] = max(mxr[i+1], arr[i]); // select maximum of right 
    } // mxr = 4 4 4 4 4 4 

    int sum =0; // for sum of water size 
    int water[n];
    for (int i =0 ; i < n ; i++) { // for water size select the Minimum and subtract 
        water[i] = (min(mxl[i] , mxr[i]) - arr[i]); // with the arr[i] ( height)
        sum += water[i]; // add one by one 
    }
    cout<< sum;

} 
*/
int solve(int n,int arr[]){
    int mxl[n];
    mxl[0] = arr[0];
    for(int i=1;i<n;i++){
        mxl[i] = max(mxl[i-1],arr[i]); 
    }
    int mxr[n];
    mxr[n-1] = arr[n-1];
    for(int i = n-2;i>=0;i--){   // n-2
        mxr[i] = max(mxr[i+1],arr[i]);
    }
    int sum =0;
    int water[n];
    for(int i=0;i<n;i++){
        water[i] = ( min(mxl[i],mxr[i]) - arr[i]);
        sum += water[i];
    }
    return sum;
    
}

int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    cout<< solve(n,arr);

} 