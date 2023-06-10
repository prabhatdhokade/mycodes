//input : 8
//2 3 1 8 2 3 5 1
//output : mis-4, dup-1  mis-6, dup-3  mis-7, dup-2

#include<bits/stdc++.h>

using namespace std;  

int main()             //this program contains  1 to N'th values (N= size of array)
{
    int n;
    cin>>n;
    int arr[n];
    for( int i =0; i< n; i++) {
        cin>>arr[i];
    }

    int i=0,j=0;
    int du;
    int mis;
    
    while (i < n) 
    {
        if(arr[i] != arr[arr[i]-1]) {    // the arr[i] should have to be equal to i+1( means arr[1] == 2 or i+1) 
            swap (arr[i], arr[arr[i]-1]); // only  this is the logic in this question
            //i++; no need to do i++
        } 
        else {
            i++;
        }
    }
    for(i= 0; i <n ;i++ ) {
       
       if ( arr[i] != i+1) {        // if they are not equal then duplicate element will be pressent at that i'th location  
        cout<< " mis-" << i+1<<",";  // and there should have the missing value of i+1
        cout<< " dup-" << arr[i]<<" ";
       }
    }
}