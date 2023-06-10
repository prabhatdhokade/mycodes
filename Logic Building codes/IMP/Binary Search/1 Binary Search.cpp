/* Given a sorted array arr[] of n elements, 
write a function to search a given element x in arr[].
time complexity is log2(n);
input : 5
1 4 7 8 9
8
output : 3  */


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

    int start = 0 ;
    int end = n - 1;

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
    }
}
*/

#include<bits/stdc++.h>
using namespace std;

int solve(int arr[],int n,int k){
    int start = 0;
    int end = n-1;
    while(start <= end){
        int mid = start + (end - start) / 2; // to get rid of integer overflow

        if(arr[mid] == k) return mid;
        else if(arr[mid] < k){
            start = mid + 1;
        }
        else if(arr[mid] > k){
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
