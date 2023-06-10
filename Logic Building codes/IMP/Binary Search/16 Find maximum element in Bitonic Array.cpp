/*FIND MAXIMUM ELEMENT IN AN BITONIC ARRAY:

Problem statement:
Given a bitonic array find the maximum value of the array. An array is said to be bitonic if it has an increasing sequence of integers followed immediately by a decreasing sequence of integers.

Example:

Input:
1 4 8 3 2

Output:
8 This Question is Exactly same as Peak element question, just twisted a little bit */ 


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

    int start = 0;
    int end = n-1;
    int ans = -1;

    while ( start <= end) {
        int mid = start + (end - start) / 2;

        if( mid > 0 && mid < n-1) { // check for boundries 
            if(arr[mid] > arr[mid -1] && arr[mid] > arr[mid+1]) {
                ans = arr[mid] ;
                break; // plz check out the video this is very IMP question
            }
            else if ( arr[mid] < arr[mid -1]) {
                end = mid -1;
            }
            else if ( arr[mid] < arr[mid +1]) {
                start = mid +1;
            }
        }

    }
    cout << ans ;

}
*/

#include<bits/stdc++.h>
using namespace std;

int solve(int arr[],int n){
    if(n==1) return arr[n];
    else if(n==2){
        if(arr[0]>arr[1]) return arr[0];
        else return arr[1];
    }
    int start =0;
    int end = n-1;
    while(start<=end){
        int mid = start + (end - start) /2;
        if(mid > 0 && mid < n-1){
            if(arr[mid] > arr[mid+1] && arr[mid] > arr[mid -1]) return arr[mid];
            else if(arr[mid+1] > arr[mid]){
                start = mid+1;
            }
            else 
                end  = mid -1;

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
    cout<<solve(arr,n);
}