/*Given an array of n elements, where each element is at most k away from
its target position, devise an algorithm that sorts in O(n log k) time. 
For example, let us consider k is 2, an element at index 7 in the sorted array,
can be at indexes 5, 6, 7, 8, 9 in the given array.

Example:
Input : arr[] = {6, 5, 3, 2, 8, 10, 9}
k = 3 
Output : arr[] = {2, 3, 5, 6, 8, 9, 10}
*/
#include<bits/stdc++.h>

using namespace std;

int main() {
    int n;
    cin >> n ;
    int arr[n];
    for(int i = 0 ; i < n ; i++ ) { // Time complexity : nlogk
        cin >> arr[i];
    }
    int k;
    cin >> k;
    
    priority_queue<int , vector<int> , greater<int>> minh; // min heap
    for( int i=0 ; i < n ; i++ ) {
        minh.push(arr[i]);

        if(minh.size() > k) { 
            cout << minh.top() << " ";
            minh.pop(); 
        }
    }
    while ( !minh.empty()) {
        cout<< minh.top() << " " ;
        minh.pop();
    }
}