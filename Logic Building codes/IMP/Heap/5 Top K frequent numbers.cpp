
#include<bits/stdc++.h>

using namespace std;

int main() {
    int n;
    cin >> n ;
    int arr[n];
    for(int i = 0 ; i < n ; i++ ) { 
        cin >> arr[i];
    }
    int k;
    cin >> k;

    unordered_map< int, int > mp; // for the count we use unordered map 
    for(int i = 0; i< n; i++ ) { 
        mp[arr[i]]++;
    }
   
    priority_queue< pair<int,int > , vector < pair < int ,int > > , greater <pair < int ,int > > >minh;
    //We have to sort acc to freq as jinki kam hogi woh upr rhke hat jayenge
        // that means we have to have  MIN HEAP
    
    for ( auto it = mp.begin(); it!= mp.end() ; it++ ) {
        minh.push({it-> second, it->first});  // we'll pass the count first then key
        if( minh.size() > k) {
            minh.pop();        // we'll pop the extra elemnts
        }
    }
    while ( !minh.empty()) {
        cout<<minh.top().second << " ";
        minh.pop();
    }
}