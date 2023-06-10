/*Given an infinite sorted array consisting 0s and 1s. 
The problem is to find the index of first ‘1’ in that array. 
As the array is infinite, therefore it is guaranteed that number ‘1’ will 
be present in the array.

Example:

Input : arr[] = {0, 0, 1, 1, 1, 1} 
Output : 2 */


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
    int ans = -1;

    while ( x > arr[end] ) { // for finding the bound of ele which lies in
        start = end ;
        end = end * 2 ;
    }
    // TOC : log of position of element


    while ( start <= end) {
        int mid = start + (end - start) / 2;

        if (arr[mid] == x) {
            ans = mid ; // int this we have to call the first occurunce equation
            end = mid - 1; 
        }
        else if ( arr[mid] > x) {
            end = mid - 1;
        }
        else if ( arr[mid] < x) {
            start = mid +1;
        }
    }
    cout << ans;

}
*/

#include<bits/stdc++.h>
using namespace std;

int solve(int arr[],int k){
    int start =0;
    int end =1;

    while(arr[end] < k){
        start =end;
        end *= 2;
    }
    int ans = -1;
    while(start<=end){
        int mid = start + (end -start) /2;
        if(arr[mid] == k){
            ans = mid;
            end = mid-1;
        }
        else if(arr[mid] < k){
            start = mid +1;
        }
        else if ( arr[mid] > k) {
            end = mid - 1;
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
    cout<<solve(arr,k);
}