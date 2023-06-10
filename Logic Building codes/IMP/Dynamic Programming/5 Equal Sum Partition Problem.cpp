/* Equal Sum Partition Problem
Partition problem is to determine whether a given set can be partitioned into 
two subsets such that the sum of elements in both subsets is same.
Examples:

arr[] = {1, 5, 11, 5}
Output: true 
The array can be partitioned as {1, 5, 5} and {11}*/


#include<bits/stdc++.h>
using namespace std;

bool solve(int arr[],int n,int W) {
    bool t[n+1][W+1]; //this is matrix declaration
    for(int i =0;i<n+1;i++) {
        for(int j =0;j<W+1;j++) {
            if(i ==0){
                t[i][j] = false;
            }
            if(j==0){
                t[i][j] = true;
            }
        }
    }
    for(int i =1;i<n+1;i++){
        for(int j=1;j<W+1;j++){
            if(arr[i-1] <= j) { // exactly same as the previous question
                t[i][j] = t[i-1][j-arr[i-1]] || t[i-1][j];
            }
            else
                t[i][j] = t[i-1][j];
        }
    }

    return t[n][W];
}

bool ans(int arr[], int n){

    int sum =0;
    for(int i =0 ;i<n;i++){
        sum += arr[i];
    }
    if(sum % 2 != 0){   // this is common sense thing
        return false;  // how can we divide it into two equal parts if the sum is odd. 
    }
    else if(sum %2 == 0) {
        return solve(arr,n,sum/2);
    }
    else 
        return false;
}
int main() 
{
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++) {
        cin>>arr[i];
    }
    cout<<ans(arr,n);
}