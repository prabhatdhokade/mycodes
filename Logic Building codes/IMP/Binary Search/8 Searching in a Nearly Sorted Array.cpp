/*SEARCH IN A NEARLY SORTED ARRAY:

Given an array which is sorted, but after sorting some elements are moved to either of 
the adjacent positions, i.e., arr[i] may be present at arr[i+1] or arr[i-1]. 
Write an efficient function to search an element in this array.
Basically the element arr[i] can only be swapped with either arr[i+1] or
arr[i-1].

For example consider the array {2, 3, 10, 4, 40}, 4 is moved to next
position and 10 is moved to previous position.

Example :
Input: arr[] =  {10, 3, 40, 20, 50, 80, 70}, key = 40
Output: 2 
Output is index of 40 in given array
*/

/*
#include<bits/stdc++.h>
using namespace std;

int main() {

    int n ;
    cin >> n;

    int arr[n];
    for(int i =0 ; i < n ; i++) {
        cin >> arr[i];
    }
    int x;
    cin>> x;

    int start = 0; 
    int end = n-1;

    while( start <= end) {
        int mid = start + (end - start) / 2 ;
        if ( arr[mid] == x) {
            cout << mid ;
        }
        else if ( mid >= start && arr[mid-1] == x ) {
            cout<< mid-1;
        }
        else if (mid <= end && arr[mid+1] == x) {
            cout<< mid+1;
        }

        if(arr[mid] < x) {
            start = mid + 2;
        }
        else 
            end = mid -2;
    }
}
*/

#include<bits/stdc++.h>
using namespace std;

int solve(int arr[],int n,int k){
    int start=0;
    int end =n-1;
    int ans = -1;
    while(start<=end)
    {
        int mid = start +(end - start)/2;

        if(arr[mid] == k){ 
            return mid;
        }
        else if( mid-1 >= start && arr[mid-1]== k){
            return mid-1;
        }
        else if( mid+1 <=end && arr[mid+1] == k) {
            return mid+1;
        }

        if(arr[mid] < k) {
            start = mid +2;
        }
        else   end = mid -2;
    }
    return ans;
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
