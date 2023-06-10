
/* Given an array and a number k where k is smaller than size of array, 
we need to find the k’th smallest element in the given array. 
It is given that all array elements are distinct.

Example:
Input: arr[] = { 7, 10, 4, 3, 20, 15 }
k = 3
Output: 7 */

#include<bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n ;
    int arr[n];
    for(int i = 0 ; i < n ; i++ ) { // only by using sorting the time complexity
        cin >> arr[i]; // will be nlogn but by this method it becomes "nlogk"
    }

    int  k;  // if there is something given like smallest,largest. k'th then
    cin >> k; // definitely heap will use there 
            // for smaller -> maxheap
            // for greater -> minheap ( vice versa)
    priority_queue<int>maxh;  // maxheap declairation

    for(int i = 0 ; i < n ; i++) { 
        maxh.push(arr[i]);
        if (maxh.size() > k ) {
            maxh.pop();
        }
    }
    cout<< maxh.top();
}