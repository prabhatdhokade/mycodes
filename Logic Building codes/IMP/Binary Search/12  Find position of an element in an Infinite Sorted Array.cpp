/* Suppose you have a sorted array of infinite numbers, 
how would you search an element in the array?

Since array is sorted, the first thing clicks into mind is binary search, but the problem here is that we don’t know size of array.
If the array is infinite, that means we don’t have proper bounds to apply binary search. So in order to find position of key, 
first we find bounds and then apply binary search algorithm.

Let low be pointing to 1st element and high pointing to 2nd element of array, Now compare key with high index element,
-if it is greater than high index element then copy high index in low index and double the high index.
-if it is smaller, then apply binary search on high and low indices found.

input : 1 2 3 4 5 6 7 8 9 10 11 12 13 ....
element : 4 
output : 3
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
    int  x;
    cin>> x;

    int start = 0;
    int end = 1;

    while ( x > arr[end] ) {
        start = end ;
        end = end * 2 ; // we get the bound of the element in which it lies 
        
    }
    //cout << start << " ";
    //cout << end << " ";

     while ( start <= end) {
        int mid = start + (end - start) / 2  ; // we can do (start + end) / 2 
                                            //but we use that one to get rid of Integer overflow;
        if( x == arr[mid] ) {  // arr[mid] is imp
            cout<< mid;
            return mid;
        }
        else if ( x < arr[mid] ) {
            end = mid-1;
        }
        else if ( x > arr[mid]) {
            start = mid + 1;
        }
        else 
            return -1;
    }
    
}
*/
#include<bits/stdc++.h>
using namespace std;

int solve(int arr[],int k){
    int start =0;
    int end =1;

    while(arr[end] < k){
        start = end;
        end *= 2;
    }
    int ans = -1;
    while(start<=end){
        int mid = start +(end - start)/2;
        if(arr[mid] == k) return mid;
        else if(arr[mid] > k){
            end = mid -1;
        }
        else if(arr[mid] < k){
            start = mid + 1;
        }
    }
    return ans;

}

int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        arr[i] = i;
    }
    int k;
    cin>>k;
    cout<<solve(arr,k);
}