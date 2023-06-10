/*FIND PEAK ELEMENT IN AN ARRAY:

A peak element is an element that is greater than its neighbors.

Given an input array nums, where nums[i] ≠ nums[i+1], find a peak element and return its index.

The array may contain multiple peaks, in that case return the index to any one of the peaks is fine.

You may imagine that nums[-1] = nums[n] = -∞.

Example :

Input: nums = [1,2,3,1]
Output: 2
Explanation: 3 is a peak element and your function should return the index number 2. */
// SOMETHING WRONG WITH CODE PLZ CHECK IT OUT

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
                ans = mid ;
                break; // plz check out the video this is very IMP question
            }
            else if ( arr[mid] < arr[mid -1]) {
                end = mid -1;
            }
            else if ( arr[mid] < arr[mid +1]) {
                start = mid +1;
            }
        }

        else if ( mid == 0) { // for first element if it is greater than arr[1] then it is peak
            if (arr[0] > arr[1]) {
                ans = 0;
            }
            else 
                ans = 1;
        }

        else if ( mid == n-1) {
            if ( arr[n-1] > arr[n-2]) {
                ans = n-1;
            }
            else 
                ans = n-2;
        }

    }
    cout << ans ;

}
*/

#include<bits/stdc++.h>
using namespace std;

int solve(int arr[],int n){
    if(n == 1) return 0;
    if(n==2){
        if(arr[0] > arr[1]) return 0;
        else return 1;      
    }
    int start =0;
    int end = n-1;
    while(start<=end){
        int mid = start + (end -start)/2;
        if(mid>0 && mid <n-1){
            if(arr[mid] > arr[mid-1] && arr[mid] > arr[mid+1]) return mid;

            else if(arr[mid+1] > arr[mid])  start =mid +1;

            else if(arr[mid-1] > arr[mid])   end = mid -1;
        }
        else if(mid == 0){
            if(arr[mid] > arr[mid+1]) return mid;
            else return mid+1;
        }
        else if(mid == n-1){
            if(arr[mid] > arr[mid-1]) return mid;
            else return mid-1;
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
