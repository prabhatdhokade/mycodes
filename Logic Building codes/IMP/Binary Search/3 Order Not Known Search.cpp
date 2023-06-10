/* Given a sorted array of numbers, find if a given number ‘key’ is present
 in the array. Though we know that the array is sorted, 
we don’t know if it’s sorted in ascending or descending order.*/
#include <bits/stdc++.h>

using namespace std;

int main() {

    int n ;
    cin >> n;

    int arr[n];
    for(int i =0 ; i < n ; i++) {
        cin >> arr[i];
    }
    int ele;
    cin >> ele;

    int start =0 ;
    int end = n - 1;

    if( arr[0] < arr[n-1]) {

        while ( start <= end) {
        int mid = start + (end - start) / 2  ; // we can do (start + end) / 2 
                                            //but we use that one to get rid of Integer overflow;
        if( ele == arr[mid] ) {  // arr[mid] is imp
            cout<< mid;
            return mid;
        }
        else if ( ele < arr[mid] ) {
            end = mid-1;
        }
        else if ( ele > arr[mid]) {
            start = mid + 1;
        }
        else 
            return -1;
        }

    }
    else 
        while ( start <= end) {
        int mid = start + (end - start) / 2  ; // we can do (start + end) / 2 
            //cout << mid << " ";                                //but we use that one to get rid of Integer overflow;
        if( ele == arr[mid] ) {  // arr[mid] is imp
            cout<< mid;
            return mid;
        }
        else if ( ele < arr[mid] ) {
            start= mid + 1;
        }
        else if ( ele > arr[mid]) {
            end = mid - 1;
        }
        else 
            return -1;
    }
}