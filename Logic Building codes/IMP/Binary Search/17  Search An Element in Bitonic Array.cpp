/*FIND AN ELEMENT IN BITONIC ARRAY:

https://www.interviewbit.com/problems/search-in-bitonic-array/

Given a bitonic sequence of n distinct elements, 
write a program to find a given element x in the bitonic sequence in O(log n) time. 
A Bitonic Sequence is a sequence of numbers which is first strictly increasing then after 
a point strictly decreasing.

Examples:

Input :  arr[] = {-3, 9, 8, 20, 17, 5, 1};
         key = 20
Output : Found at index 3 */

/*
#include <bits/stdc++.h>
using namespace std;
//in bitonic array,after peak element both sides always sorted,
// only the difference is left array in sorted in ascending order but the right one is in
// descending order.
// *IN Bitonic array ther's only one Peak Element*/

/*
#include<bits/stdc++.h>
using namespace std;

int main () {
    int n ;
    cin >> n;
    int arr[n];
    for(int i =0 ; i < n ; i++) {
        cin >> arr[i];
    }

    int x;
    cin >> x;
    int start = 0;
    int end = n-1;
    int ans = -1; // first find the peak element

    while ( start <= end) {
        int mid = start + (end - start) / 2;

        if( mid > 0 && mid < n-1) { // check for boundries 
            if(arr[mid] > arr[mid -1] && arr[mid] > arr[mid+1]) {
                ans = mid;
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
    int low1 = 0;
    int hig1 = ans -1; 
    int low2 = ans;
    int hig2 = n-1;
    int ans1 = -1; // now check if key is present in left array 
    int ans2 = -1;// or right array

    // for ascending order
    while ( low1 <= hig1) {
        int mid = low1 + ( hig1 - low1) / 2 ;
        if ( arr[mid] == x) {
            ans1 = mid;
            break;
        }
        else if ( arr[mid] > x ) {
            hig1 = mid -1 ;
        }
        else if ( arr[mid] < x) {
            low1 = mid + 1;
        }
    }
    // for descending order
    while ( low2 <= hig2) {
        int mid = low2 + ( hig2 - low2) / 2 ;
        if ( arr[mid] == x) {
            ans2 = mid;
            break;
        }
        else if ( arr[mid] > x ) {
            hig2 = mid -1 ;
        }
        else if ( arr[mid] < x) {
            low2 = mid + 1;
        }
    }

    if (ans1 != -1){
        cout<<ans1;
    }
    else if( ans2 != -1) {
        cout << ans2;
    }
    else 
        cout<<-1;


}
*/

#include<bits/stdc++.h>
using namespace std;
int solve(int arr[],int n,int k){
    int start =0;
    int end =n-1;
    int ans = -1;
    while(start<=end){
        int mid = start + (end - start) /2;
        if(mid > 0 && mid < n-1){
            if(arr[mid] > arr[mid-1] && arr[mid] > arr[mid+1]) {
                ans = mid; 
                break;
            }
            else if(arr[mid - 1] > arr[mid] ) end = mid -1;
            else  start = mid + 1;
        }
    }
    int start1 = 0;
    int end1 = ans;
    int start2 = ans +1;
    int end2 = n-1;
    int ans2 =-1;

    while(start1<=end1){
        int mid = start1 +(end1 - start1)/2;
        if(arr[mid] == k) return mid;
        else if(arr[mid] < k) start1 = mid +1;   // different steps
        else  end1 =mid -1;
    }
    while(start2<=end2){
        int mid = start2 +(end2 - start2)/2;
        if(arr[mid] == k) return mid;
        else if(arr[mid] < k) end2 = mid -1; // different steps
        else  start2 =mid +1;
    }
    return ans2;
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