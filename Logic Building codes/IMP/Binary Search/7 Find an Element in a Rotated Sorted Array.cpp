/*FIND AN ELEMENT IN A ROTATED SORTED ARRAY:

Suppose an array sorted in ascending order is rotated at some pivot unknown to you beforehand.

(i.e., [0,1,2,4,5,6,7] might become [4,5,6,7,0,1,2]).

You are given a target value to search. If found in the array return its index, otherwise return -1.

You may assume no duplicate exists in the array.

Your algorithm's runtime complexity must be in the order of O(log n).

Example:

Input: nums = [4,5,6,7,0,1,2], target = 0
Output: 4
  
*/

#include<bits/stdc++.h>
using namespace std;

int bs(int arr[],int s,int n,int k){
    int start = s;
    int end = n-1;
    cout<<"1a ";
    while(start<=end){
        int mid = start+(end-start)/2;
        if(arr[mid] == k) {
            cout<<mid<<" ";
            return mid;
        }
        else if(arr[mid] > k){
            end = mid -1;
        }
        else if(arr[mid] < k){
            start = mid +1;
        }
    }
    return -1;
}

int solve(int arr[],int n,int k){
    int start =0;
    int end =n-1;
    int i=0;
    while(start<=end){
        int mid = start +(end-start)/2;
        int next = (mid+1)%n;
        int pre = (mid-1+n)%n;
        if(arr[mid] < arr[next] && arr[mid] < arr[pre]){
            i = mid;
            cout<<mid<<" ";
            break;
        }
        else if(arr[mid] >=arr[next]){
            start = mid+1;
        }
        else if(arr[mid] >=arr[pre]){
            end = mid -1;
        }
    }
    cout<<i<<" ";
    int a = bs(arr,0,i,k);
    int b = bs(arr,i,n,k);
    if(a != -1) return a;
    if(b != -1) return b;
    return -1;
}

int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    int k;
    cin>>k;
    cout<<solve(arr,n,k);
}