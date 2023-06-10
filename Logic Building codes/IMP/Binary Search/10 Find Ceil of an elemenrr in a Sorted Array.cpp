/* CEILING OF AN ELEMENT IN A SORTED ARRAY:

Given a sorted array and a value x, the ceiling of x is the smallest element in array greater than or equal to x, and the floor is the greatest element smaller than or equal to x. Assume than the array is sorted in non-decreasing order. Write efficient functions to find floor and ceiling of x.

Examples :

For example, let the input array be {1, 2, 8, 10, 10, 12, 19}
For x = 0:    floor doesn't exist in array,  ceil  = 1
For x = 1:    floor  = 1,  ceil  = 1
For x = 5:    floor  = 2,  ceil  = 8
For x = 20:   floor  = 19,  ceil doesn't exist in array
*/

/*
#include <bits/stdc++.h>

using namespace std;

int main () {
    int n ;
    cin >> n;

    int arr[n];
    for(int i =0 ; i < n ; i++) {
        cin >> arr[i];
    }
    int x;
    cin>> x;
    // ceil = smallest  element just greater than x.
    int start = 0 ;
    int end = n-1;
    int res = -1;

    while ( start <= end) {
        int mid = start + (end-start) /2 ;

        if ( arr[mid] == x) {
            res = arr[mid];  
            break;
        }
        if ( arr[mid] < x) {  
            start = mid + 1;
        }
        else if (arr[mid] > x) {
            res = arr[mid]; // // this is IMP, the greater ele than x can be the possible ans.
            //we want ceil of that element means the element can 
            // be greater or equal to that element.
            end = mid -1 ;
        }
    }

    cout << res ;

}
*/

#include<bits/stdc++.h>
using namespace std;

int solve(int arr[],int n,int k){
    int start =0;
    int end = n-1;
    int ans = -1;
    while(start<=end){
        int mid = start +(end - start)/2;
        if(arr[mid] == k) return arr[mid];
        else if(arr[mid] > k){
            ans = arr[mid];
            end = mid -1;
        }
        else if(arr[mid] < k){
            start = mid +1;
        }
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