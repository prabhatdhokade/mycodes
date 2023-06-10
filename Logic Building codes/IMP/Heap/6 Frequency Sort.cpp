/* Print the elements of an array in the increasing frequency if 2 numbers have same frequency then print the one which came first.

Example:
Input : arr[] = {2, 5, 2, 8, 5, 6, 8, 8}
Output : arr[] = {8, 8, 8, 2, 2, 5, 5, 6}*/
// our output: 8 8 8 5 5 2 2    we have to give it with the order
#include<bits/stdc++.h>

using namespace std;

int main() {
    int n;
    cin >> n ;
    int arr[n];
    for(int i = 0 ; i < n ; i++ ) { 
        cin >> arr[i];
    }

    unordered_map< int, int > mp; // for the count we use unordered map 
    for(int i = 0; i< n; i++ ) { 
        mp[arr[i]]++;
    }
   
    priority_queue< pair<int,int > > maxh;
    //We have to sort acc to freq as jinki max hogi woh upr rhke hat jayenge
        // that means we have to have  max HEAP
    
    for ( auto it = mp.begin(); it!= mp.end() ; it++ ) {
        maxh.push({it-> second, it->first});  
        
        // we'll pass the count first then key
    }
    while ( !maxh.empty()) {
        int freq = maxh.top().first;
        int key = maxh.top().second;
        for (int i =1 ; i <= freq ; i++) {
        cout<< key << " ";
        }
        maxh.pop();
    }
}