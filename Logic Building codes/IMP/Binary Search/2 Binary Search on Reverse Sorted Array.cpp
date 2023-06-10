/* BINARY SEARCH ON REVERSE SORTED ARRAY:

Let's suppose that we have an array sorted in descending order and 
we want to find index of an element e within this array. Binary search in every step picks the middle element (m) 
of the array and compares it to e.
 If these elements are equal, than it returns the index of m. If e is greater than m, 
 than e must be located in the left subarray. On the contrary, 
 if m greater than e, e must be located in the right subarray.
  At this moment binary search repeats the step on the respective subrarray.
Because the algoritm splits in every step the array in half (and one half of the array is never processed) the input element must be located (or determined missing) in at most \\log_{2}{n} steps.

*/

/*
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
    int end = n- 1;

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
*/

#include<bits/stdc++.h>
using namespace std;

int solve(int arr[],int n,int k){
    int start = 0;
    int end = n-1;
    while(start <= end){
        int mid = start +(end- start) /2;
        if(arr[mid] == k) return mid;
        else if(arr[mid] > k){
            start = mid+1;
        }
        else if(arr[mid] < k){
            end = mid -1;
        }
    }
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