/* Given an array of integers and two numbers k1 and k2. Find the sum of all elements 
between given two k1’th and k2’th smallest elements of the array. 
It may  be assumed that all elements of array are distinct.

Example :
Input : arr[] = {20, 8, 22, 4, 12, 10, 14},  k1 = 3,  k2 = 6  
Output : 26          
         3rd smallest element is 10. 6th smallest element 
         is 20. Sum of all element between k1 & k2 is
         12 + 14 = 26*/

#include<bits/stdc++.h>

using namespace std;

int minheap( int arr[],int a , int n ) {
    priority_queue <int > maxh ;

    for(int i =0 ; i < n ; i++) {

        maxh.push(arr[i]);

        if (maxh.size() > a) {
            maxh.pop();
        }
    }
    //cout<< minh.top()<< " ";
    return maxh.top();

}

int main() {
    int n;
    cin >> n ;
    int arr[n];
    for(int i = 0 ; i < n ; i++ ) { 
        cin >> arr[i];
    }

    int k1,k2;
    cin >> k1 ;
    cin >> k2;
    int sum =0;

    int f1 = minheap(arr, k1 ,n);
    int f2 = minheap(arr, k2 ,n);
    //cout << f1 <<" " << f2;

    for(int i =0 ; i < n ; i++) {

        if( arr[i] > f1 && arr[i] < f2) {
            sum = sum + arr[i];
        }
    }
   cout<< sum;


}