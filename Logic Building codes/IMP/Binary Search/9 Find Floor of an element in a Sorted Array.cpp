/* FIND FLOOR OF AN ELEMENT IN A SORTED ARRAY:

Given a sorted array and a value x, the floor of x is the largest element in 
array smaller than or equal to x. Write efficient functions to find floor of x.

Example:

Input : arr[] = {1, 2, 8, 10, 10, 12, 19}, x = 5
Output : 2
2 is the largest element in arr[] smaller than 5.*/

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
    // floor = greatest element smaller than x
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
            res = arr[mid]; // this is IMP, the smaller ele than x can be the possible ans.
            //we want floor of that element means the element can -
            start = mid + 1;// be smaller or equal to that element.
        }
        else if (arr[mid] > x) {
            end = mid -1 ;
        }
    }

    cout << res ;
 
} */

#include<bits/stdc++.h>
using namespace std;

int solve(int arr[],int n,int k){
    int start =0;
    int end = n-1;
    int ans = -1;
    while(start<=end){
        int mid = start + (end - start)/2;
        if(arr[mid] == k) return arr[mid];
        else if(arr[mid] < k){
            ans = arr[mid];
            start = mid +1;
        }
        else if(arr[mid] > k){
            end = mid -1;
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