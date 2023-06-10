/*COUNT NUMBER OF OCURRENCES(or frequency) IN A SORTED ARRAY:

Given a sorted array arr[] and a number x, 
write a function that counts the occurrences of x in arr[]. 
Expected time complexity is O(Logn)
Examples:
  Input: arr[] = {1, 1, 2, 2, 2, 2, 3,},   x = 2
  Output: 4 // x (or 2) occurs 4 times in arr[]

  Input: arr[] = {1, 1, 2, 2, 2, 2, 3,},   x = 3
Output: 1  */


#include<bits/stdc++.h>
using namespace std;

int solve(int arr[],int n,int k){
    int start = 0;
    int end = n-1;
    int first = 0;
    int last = -1;
    int count = 0;
    while(start<=end){
        int mid = start +(end - start)/2;
        if(arr[mid] == k){
            first = mid;
            end = mid -1;
        }
        else if(arr[mid] < k) start = mid+1;
        else if(arr[mid] > k) end = mid-1;
    }
    start = 0;
    end = n-1;
    while(start<=end){
        int mid = start +(end - start)/2;
        if(arr[mid] == k){
            last = mid;
            start = mid +1;
        }
        else if(arr[mid] < k) start = mid+1;

        else if(arr[mid] > k) end = mid-1;
    }
    count = last - first + 1;
    return count;
}

int main()
{
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