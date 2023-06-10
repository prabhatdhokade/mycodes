/* Find the Rotation Count in Rotated Sorted array
Consider an array of distinct numbers sorted in increasing order. The array has been rotated (clockwise) k number of times. Given such an array, find the value of k.

Examples:

Input : arr[] = {15, 18, 2, 3, 6, 12}
Output: 2
Explanation : Initial array must be {2, 3,
6, 12, 15, 18}. We get the given array after 
rotating the initial array twice.

Input : arr[] = {7, 9, 11, 12, 5}
Output: 4

Input: arr[] = {7, 9, 11, 12, 15}
Output: 0
*/

/*

#include <bits/stdc++.h>
using namespace std;

int rotated( int arr[], int n) {
    int count = 0 ;
    int start = 0;
    int end = n-1;
    while( start <= end) {
        int mid = start + (end - start) / 2;
        int next = (mid + 1) % n;   // we use % bcoz we should not go out of our boundry
        int pre = (mid + n - 1) % n ; // try test  case using at index 0 and last(n)

        if (arr[mid] < arr[next] && arr[mid] <  arr[pre] ) {
            return mid;
        }  
        else if (arr[next] < arr[mid]) {
            start = mid + 1;   
        }
        else if (arr[mid] > arr[pre]) {
            end = mid - 1;
        }
    }
    return count;
} 

int main() 
{
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++) {
        cin>>arr[i];
    }
    int count = rotated(arr,n);
    cout << count; 
}
*/

#include<bits/stdc++.h>
using namespace std;

int solve(int arr[],int n){
    int start =0;
    int end = n-1;
    int count =0;
    if(arr[0]<arr[n-1]) return arr[0];
    while(start<=end){
        int mid = start +(end-start)/2;
        cout<<mid<<" ";
        int next = (mid+1)% n;
        cout<<next<<"n ";   // array out of bound
        int pre  = (mid -1+n)% n; // array out of bound
        cout<<pre<<"p ";
        if(arr[mid] < arr[next] && arr[mid] < arr[pre]){
            cout<< mid<<"ans ";
        }
        else if(arr[mid] >= arr[0]){
            start = mid +1; 
            cout<<start<<"S ";
        }
        else if (arr[mid] >= arr[n-1]){
            end = mid-1;
            cout<<end<<"E ";
        }
    }
    return count;
}

int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    cout<<solve(arr,n);
}
